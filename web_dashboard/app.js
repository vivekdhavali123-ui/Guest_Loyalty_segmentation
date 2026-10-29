/**
 * Accor Live Limitless (ALL) - AI Segmentation & Churn Prevention Dashboard
 * Frontend Application Logic & Chart Orchestration
 */

let dashboardData = null;
let charts = {};
let filteredMembers = [];

// Color Palette Constants
const COLORS = {
    gold: '#c5a059',
    goldBright: '#dfba6a',
    red: '#ef4444',
    amber: '#f59e0b',
    green: '#10b981',
    cyan: '#06b6d4',
    navyDark: '#0f1523',
    slate: '#64748b',
    textMuted: '#94a3b8'
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        const response = await fetch("dashboard_data.json");
        if (!response.ok) throw new Error("Network response was not ok");
        dashboardData = await response.json();
    } catch (err) {
        console.warn("Could not fetch dashboard_data.json via HTTP, initializing fallback embedded bundle:", err);
        dashboardData = getFallbackData();
    }
    
    renderKpis();
    renderOverviewCharts();
    renderSegmentCards();
    renderClusterTable();
    renderModelSummary();
    renderFeatureImportanceChart();
    populateMemberList();
    initSimulation();
}

function renderKpis() {
    if (!dashboardData || !dashboardData.kpis) return;
    const kpis = dashboardData.kpis;
    
    document.getElementById("kpiTotalMembers").innerText = (kpis.total_active_loyalty_members || 12000).toLocaleString();
    document.getElementById("kpiTotalSpend").innerText = "€" + ((kpis.total_portfolio_revenue_eur || 34941337) / 1000000).toFixed(2) + "M";
    document.getElementById("kpiAvgSpend").innerText = "€" + Math.round(kpis.average_member_spend_eur || 2912).toLocaleString();
    document.getElementById("kpiChurnRate").innerText = (kpis.overall_churn_rate_pct || 25.14).toFixed(1) + "%";
    document.getElementById("kpiHighRiskCount").innerText = (kpis.high_risk_member_count || 3017).toLocaleString();
    document.getElementById("kpiSpendAtRisk").innerText = "€" + Math.round(kpis.high_value_revenue_at_stake_eur || 402343).toLocaleString();
    document.getElementById("kpiRoi").innerText = (kpis.projected_campaign_roi_pct || 904.6).toFixed(1) + "%";
    document.getElementById("kpiRecoveredRev").innerText = "€" + Math.round((kpis.projected_campaign_recovered_revenue_eur || 502309) / 1000).toLocaleString() + "K";
}

function renderOverviewCharts() {
    if (!dashboardData) return;

    // 1. Segment Revenue Bar Chart
    const ctxSegment = document.getElementById("segmentRevenueChart");
    if (ctxSegment) {
        const segLabels = dashboardData.segments.map(s => s.segment_name);
        const segRevs = dashboardData.segments.map(s => s.total_spend_eur / 1000000);
        
        charts.segmentRevenue = new Chart(ctxSegment, {
            type: "bar",
            data: {
                labels: segLabels,
                datasets: [{
                    label: "Total Revenue (€ Millions)",
                    data: segRevs,
                    backgroundColor: [
                        'rgba(223, 186, 106, 0.85)',
                        'rgba(6, 182, 212, 0.75)',
                        'rgba(16, 185, 129, 0.75)',
                        'rgba(245, 158, 11, 0.75)',
                        'rgba(239, 68, 68, 0.75)'
                    ],
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` €${ctx.parsed.y.toFixed(2)}M EUR`
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: COLORS.textMuted, font: { size: 11 } },
                        grid: { display: false }
                    },
                    y: {
                        ticks: {
                            color: COLORS.textMuted,
                            callback: (v) => `€${v}M`
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                }
            }
        });
    }

    // 2. Loyalty Tier Donut
    const ctxTier = document.getElementById("tierDonutChart");
    if (ctxTier) {
        charts.tierDonut = new Chart(ctxTier, {
            type: "doughnut",
            data: {
                labels: dashboardData.tiers.map(t => t.tier_name),
                datasets: [{
                    data: dashboardData.tiers.map(t => t.count),
                    backgroundColor: ['#38bdf8', '#94a3b8', '#facc15', '#64748b', '#475569'],
                    borderColor: '#0f1523',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: COLORS.textMuted, boxWidth: 12, font: { size: 11 } }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 3. Churn Risk Donut
    const ctxRisk = document.getElementById("churnRiskDonutChart");
    if (ctxRisk) {
        const riskDist = dashboardData.risk_distribution || { "High Risk": 3017, "Medium Risk": 3, "Low Risk": 8980 };
        charts.riskDonut = new Chart(ctxRisk, {
            type: "doughnut",
            data: {
                labels: Object.keys(riskDist),
                datasets: [{
                    data: Object.values(riskDist),
                    backgroundColor: [COLORS.red, COLORS.amber, COLORS.green],
                    borderColor: '#0f1523',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: COLORS.textMuted, boxWidth: 12, font: { size: 11 } }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 4. Booking Channel Disintermediation
    const ctxChannel = document.getElementById("channelShareChart");
    if (ctxChannel) {
        charts.channel = new Chart(ctxChannel, {
            type: "pie",
            data: {
                labels: ["Direct ALL App / Web", "Third-Party OTAs (Expedia/Booking)"],
                datasets: [{
                    data: [70.3, 29.7],
                    backgroundColor: [COLORS.gold, 'rgba(255, 255, 255, 0.15)'],
                    borderColor: '#0f1523',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: COLORS.textMuted, boxWidth: 12 }
                    }
                }
            }
        });
    }
}

function renderSegmentCards() {
    const grid = document.getElementById("segmentCardsGrid");
    if (!grid || !dashboardData) return;

    grid.innerHTML = "";
    dashboardData.segments.forEach(seg => {
        const isHighRisk = seg.churn_rate_pct > 30;
        const card = document.createElement("div");
        card.className = "segment-card";
        card.innerHTML = `
            <div class="segment-header">
                <span class="segment-title">${seg.segment_name}</span>
                <span class="segment-badge ${isHighRisk ? 'badge-risk-high' : 'badge-risk-low'}">
                    ${seg.churn_rate_pct}% Churn
                </span>
            </div>
            <div class="segment-stat-row">
                <span class="stat-label">Member Count:</span>
                <span class="stat-val">${seg.member_count.toLocaleString()} (${seg.pct_members}%)</span>
            </div>
            <div class="segment-stat-row">
                <span class="stat-label">Total Portfolio Spend:</span>
                <span class="stat-val text-gold">€${Math.round(seg.total_spend_eur).toLocaleString()}</span>
            </div>
            <div class="segment-stat-row">
                <span class="stat-label">Average Spend / Guest:</span>
                <span class="stat-val">€${Math.round(seg.avg_spend_eur).toLocaleString()}</span>
            </div>
            <div class="segment-stat-row">
                <span class="stat-label">Average Recency:</span>
                <span class="stat-val">${seg.avg_recency_days} Days</span>
            </div>
            <div class="segment-stat-row">
                <span class="stat-label">Completed Stays:</span>
                <span class="stat-val">${seg.avg_stays} Stays</span>
            </div>
            <div class="segment-stat-row">
                <span class="stat-label">Average Churn Score:</span>
                <span class="stat-val ${seg.avg_churn_score >= 50 ? 'text-red' : 'text-green'}">
                    ${seg.avg_churn_score} / 100
                </span>
            </div>
        `;
        grid.appendChild(card);
    });
}

function renderClusterTable() {
    const tbody = document.getElementById("clusterTableBody");
    if (!tbody || !dashboardData) return;
    
    tbody.innerHTML = "";
    dashboardData.segments.forEach((seg, idx) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>Cluster ${idx}:</strong> ${seg.segment_name}</td>
            <td>${seg.member_count.toLocaleString()}</td>
            <td>${seg.pct_members}%</td>
            <td>${seg.avg_recency_days}d</td>
            <td>${seg.avg_stays}</td>
            <td class="text-gold">€${Math.round(seg.avg_spend_eur).toLocaleString()}</td>
            <td><span class="${seg.avg_churn_score >= 50 ? 'text-red' : 'text-green'} font-weight-bold">${seg.avg_churn_score}</span></td>
            <td><span class="${seg.churn_rate_pct > 30 ? 'badge-risk-high' : 'badge-risk-low'}">${seg.churn_rate_pct}%</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function renderModelSummary() {
    if (!dashboardData) return;
    const model = dashboardData.champion_model || "XGBoost Classifier";
    const metrics = dashboardData.model_metrics || { roc_auc: 1.0, pr_auc: 0.9999, precision: 0.9967, recall: 1.0, f1_score: 0.9983 };

    document.getElementById("championModelName").innerText = `Champion Model: ${model}`;
    document.getElementById("modelRocAuc").innerText = metrics.roc_auc.toFixed(4);
    document.getElementById("modelPrAuc").innerText = metrics.pr_auc.toFixed(4);
    document.getElementById("modelPrecision").innerText = (metrics.precision * 100).toFixed(2) + "%";
    document.getElementById("modelRecall").innerText = (metrics.recall * 100).toFixed(2) + "%";
    document.getElementById("modelF1").innerText = metrics.f1_score.toFixed(4);
}

function renderFeatureImportanceChart() {
    const ctx = document.getElementById("featureImportanceChart");
    if (!ctx || !dashboardData) return;

    const feats = dashboardData.feature_importances || [];
    const labels = feats.map(f => f.feature);
    const vals = feats.map(f => f.importance_pct);

    charts.featureImp = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Feature Importance (%)",
                data: vals,
                backgroundColor: 'rgba(197, 160, 89, 0.85)',
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (c) => ` ${c.parsed.x.toFixed(2)}% Impact`
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: COLORS.textMuted, callback: (v) => `${v}%` },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    ticks: { color: COLORS.textMuted, font: { size: 11 } },
                    grid: { display: false }
                }
            }
        }
    });
}

// --------------------------------------------------------------------------
// Member List & Filtering
// --------------------------------------------------------------------------
function populateMemberList() {
    if (!dashboardData || !dashboardData.members) return;
    filteredMembers = [...dashboardData.members];
    filterMemberList();
}

function filterMemberList() {
    const search = document.getElementById("memberSearchInput").value.toLowerCase();
    const riskFilter = document.getElementById("filterRiskTier").value;
    const segFilter = document.getElementById("filterSegment").value;
    const tierFilter = document.getElementById("filterTier").value;

    const matched = dashboardData.members.filter(m => {
        const matchSearch = !search || 
            m.name.toLowerCase().includes(search) || 
            m.email.toLowerCase().includes(search) || 
            m.member_id.toLowerCase().includes(search);
        
        const matchRisk = riskFilter === "ALL" || m.risk_tier === riskFilter;
        const matchSeg = segFilter === "ALL" || m.segment === segFilter;
        const matchTier = tierFilter === "ALL" || m.tier === tierFilter;

        return matchSearch && matchRisk && matchSeg && matchTier;
    });

    renderMemberTable(matched);
}

function renderMemberTable(members) {
    const tbody = document.getElementById("crmMembersTableBody");
    const countBadge = document.getElementById("memberCountBadge");
    if (!tbody) return;

    countBadge.innerText = members.length;
    tbody.innerHTML = "";

    if (members.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; color: var(--text-muted); padding: 2rem;">No matching members found for current filters.</td></tr>`;
        return;
    }

    members.slice(0, 50).forEach(m => {
        const tr = document.createElement("tr");
        const isHigh = m.risk_tier === "High Risk";
        tr.innerHTML = `
            <td><code>${m.member_id}</code></td>
            <td><strong>${m.name}</strong></td>
            <td><span class="badge-tier tier-${m.tier.toLowerCase()}">${m.tier}</span></td>
            <td>${m.segment}</td>
            <td>${m.recency_days}d</td>
            <td class="text-gold">€${Math.round(m.spend_eur).toLocaleString()}</td>
            <td><strong class="${isHigh ? 'text-red' : 'text-green'}">${m.churn_score}</strong></td>
            <td><span class="${isHigh ? 'badge-risk-high' : 'badge-risk-low'}">${m.risk_tier}</span></td>
            <td>${m.action_title.length > 30 ? m.action_title.substring(0, 30) + '...' : m.action_title}</td>
            <td><span class="channel-badge">${m.channel}</span></td>
            <td><button class="btn-inspect" onclick="openGuestDrawer('${m.member_id}')">Playbook</button></td>
        `;
        tbody.appendChild(tr);
    });
}

// --------------------------------------------------------------------------
// Guest Drawer
// --------------------------------------------------------------------------
function openGuestDrawer(memberId) {
    const member = dashboardData.members.find(m => m.member_id === memberId);
    if (!member) return;

    document.getElementById("drawerGuestName").innerText = member.name;
    document.getElementById("drawerMemberId").innerText = `${member.member_id} • ${member.email}`;
    document.getElementById("drawerTier").innerText = member.tier;
    document.getElementById("drawerTier").className = `badge badge-tier tier-${member.tier.toLowerCase()}`;
    document.getElementById("drawerSegment").innerText = member.segment;
    document.getElementById("drawerSpend").innerText = "€" + Math.round(member.spend_eur).toLocaleString();
    document.getElementById("drawerStays").innerText = `${member.frequency_stays} Stays`;
    document.getElementById("drawerRecency").innerText = `${member.recency_days} Days Ago`;
    document.getElementById("drawerCountry").innerText = member.country;

    document.getElementById("drawerRiskScore").innerText = member.churn_score;
    const isHigh = member.risk_tier === "High Risk";
    document.getElementById("drawerRiskTier").innerText = member.risk_tier;
    document.getElementById("drawerRiskTier").className = isHigh ? "text-red" : "text-green";
    document.getElementById("drawerRiskCircle").style.borderColor = isHigh ? COLORS.red : COLORS.green;
    document.getElementById("drawerRiskCircle").style.color = isHigh ? COLORS.red : COLORS.green;
    document.getElementById("drawerRiskFactors").innerText = member.risk_factors;

    document.getElementById("drawerActionTitle").innerText = member.action_title;
    document.getElementById("drawerChannel").innerText = member.channel;
    document.getElementById("drawerIncentive").innerText = member.incentive;
    document.getElementById("drawerUrgency").innerText = member.urgency;
    document.getElementById("drawerClv").innerText = "€" + Math.round(member.clv_eur).toLocaleString() + " EUR";

    document.getElementById("guestDrawer").classList.add("open");
    document.getElementById("drawerBackdrop").style.display = "block";
}

function closeGuestDrawer() {
    document.getElementById("guestDrawer").classList.remove("open");
    document.getElementById("drawerBackdrop").style.display = "none";
}

function triggerCrmAction() {
    alert("Campaign action dispatched successfully to Accor CRM / ALL Marketing Engine for this guest!");
    closeGuestDrawer();
}

// --------------------------------------------------------------------------
// Retention Simulator
// --------------------------------------------------------------------------
function initSimulation() {
    runSimulation();
}

function runSimulation() {
    const audience = parseInt(document.getElementById("simAudience").value);
    const cost = parseFloat(document.getElementById("simCost").value);
    const upliftPct = parseFloat(document.getElementById("simUplift").value);
    const avgClv = parseFloat(document.getElementById("simClv").value);

    document.getElementById("simAudienceDisplay").innerText = audience.toLocaleString();
    document.getElementById("simCostDisplay").innerText = "€" + cost.toFixed(2);
    document.getElementById("simUpliftDisplay").innerText = upliftPct + "%";
    document.getElementById("simClvDisplay").innerText = "€" + avgClv.toLocaleString();

    const totalCost = audience * cost;
    const retainedGuests = Math.round(audience * (upliftPct / 100));
    const recoveredRevenue = retainedGuests * avgClv;
    const netProfit = recoveredRevenue - totalCost;
    const netRoi = totalCost > 0 ? (netProfit / totalCost) * 100 : 0;

    document.getElementById("simTotalCost").innerText = "€" + Math.round(totalCost).toLocaleString();
    document.getElementById("simRetainedCount").innerText = `${retainedGuests.toLocaleString()} Guests`;
    document.getElementById("simRecoveredRevenue").innerText = "€" + Math.round(recoveredRevenue).toLocaleString();
    document.getElementById("simNetRoi").innerText = netRoi.toFixed(1) + "%";

    updateSimChart(totalCost, recoveredRevenue);
}

function updateSimChart(cost, revenue) {
    const ctx = document.getElementById("simComparisonChart");
    if (!ctx) return;

    if (charts.simComparison) {
        charts.simComparison.destroy();
    }

    charts.simComparison = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Campaign Investment", "Recovered CLV Revenue (24M)"],
            datasets: [{
                data: [cost, revenue],
                backgroundColor: [COLORS.amber, COLORS.green],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (c) => ` €${Math.round(c.parsed.y).toLocaleString()} EUR`
                    }
                }
            },
            scales: {
                x: { ticks: { color: COLORS.textMuted }, grid: { display: false } },
                y: {
                    ticks: {
                        color: COLORS.textMuted,
                        callback: (v) => `€${Math.round(v / 1000)}k`
                    },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                }
            }
        }
    });
}

// --------------------------------------------------------------------------
// Navigation & Utilities
// --------------------------------------------------------------------------
function switchTab(tabId) {
    document.querySelectorAll(".tab-button").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(content => content.classList.remove("active"));

    const tabMap = {
        'overviewTab': 'tabBtnOverview',
        'segmentationTab': 'tabBtnSegmentation',
        'churnModelTab': 'tabBtnChurn',
        'crmActionTab': 'tabBtnCrm',
        'simulatorTab': 'tabBtnSim'
    };

    const targetBtn = document.getElementById(tabMap[tabId]);
    if (targetBtn) targetBtn.classList.add("active");

    const targetTab = document.getElementById(tabId);
    if (targetTab) targetTab.classList.add("active");
}

function refreshDashboard() {
    loadDashboardData();
}

function exportPrioritizedAudience() {
    if (!dashboardData || !dashboardData.members) return;

    const highRisk = dashboardData.members.filter(m => m.risk_tier === "High Risk");
    const headers = ["Member_ID", "Name", "Email", "Tier", "Segment", "Churn_Risk_Score", "Total_Spend_EUR", "Recommended_Action", "Channel", "Incentive_Offer"];
    
    let csvContent = "data:text/csv;charset=utf-8," + headers.join(",") + "\n";
    highRisk.forEach(m => {
        const row = [
            m.member_id,
            `"${m.name}"`,
            m.email,
            m.tier,
            `"${m.segment}"`,
            m.churn_score,
            m.spend_eur,
            `"${m.action_title}"`,
            `"${m.channel}"`,
            `"${m.incentive}"`
        ];
        csvContent += row.join(",") + "\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Accor_CRM_Prioritized_Retention_Audience_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Fallback embedded bundle in case of offline file:// protocol viewing
function getFallbackData() {
    return {
        kpis: {
            total_active_loyalty_members: 12000,
            total_portfolio_revenue_eur: 34941337.88,
            average_member_spend_eur: 2911.78,
            overall_churn_rate_pct: 25.14,
            high_risk_member_count: 3017,
            high_risk_member_pct: 25.14,
            total_revenue_at_risk_eur: 2790607.95,
            high_value_revenue_at_stake_eur: 402343.04,
            estimated_clv_at_risk_eur: 357993.31,
            projected_campaign_recovered_revenue_eur: 502309.43,
            projected_campaign_roi_pct: 904.6
        },
        champion_model: "XGBoost Classifier",
        model_metrics: {
            accuracy: 0.9992,
            roc_auc: 1.0000,
            pr_auc: 0.9999,
            precision: 0.9967,
            recall: 1.0000,
            f1_score: 0.9983
        },
        segments: [
            { segment_name: "High-Value Champions", member_count: 3013, pct_members: 25.1, total_spend_eur: 24751795, avg_spend_eur: 8215, avg_recency_days: 57.5, avg_stays: 8.6, avg_churn_score: 3.4, churn_rate_pct: 0.0, high_risk_count: 0 },
            { segment_name: "Dormant / Churned", member_count: 3201, pct_members: 26.7, total_spend_eur: 7048602, avg_spend_eur: 2202, avg_recency_days: 341.4, avg_stays: 4.7, avg_churn_score: 64.2, churn_rate_pct: 36.1, high_risk_count: 1155 },
            { segment_name: "Loyal Mainstays", member_count: 3384, pct_members: 28.2, total_spend_eur: 1834128, avg_spend_eur: 542, avg_recency_days: 293.7, avg_stays: 1.7, avg_churn_score: 52.8, churn_rate_pct: 30.7, high_risk_count: 1039 },
            { segment_name: "At-Risk High-Spenders", member_count: 2135, pct_members: 17.8, total_spend_eur: 1303812, avg_spend_eur: 611, avg_recency_days: 299.0, avg_stays: 1.8, avg_churn_score: 53.6, churn_rate_pct: 30.9, high_risk_count: 660 },
            { segment_name: "Value Seekers", member_count: 267, pct_members: 2.2, total_spend_eur: 3000, avg_spend_eur: 11, avg_recency_days: 337.3, avg_stays: 0.0, avg_churn_score: 72.1, churn_rate_pct: 60.7, high_risk_count: 163 }
        ],
        tiers: [
            { tier_name: "Diamond", count: 240, total_spend: 3100000, avg_spend: 12916, churn_rate: 8.3 },
            { tier_name: "Platinum", count: 960, total_spend: 7800000, avg_spend: 8125, churn_rate: 14.5 },
            { tier_name: "Gold", count: 1800, total_spend: 9200000, avg_spend: 5111, churn_rate: 22.0 },
            { tier_name: "Silver", count: 2760, total_spend: 6400000, avg_spend: 2318, churn_rate: 27.5 },
            { tier_name: "Classic", count: 6240, total_spend: 8441337, avg_spend: 1352, churn_rate: 28.8 }
        ],
        risk_distribution: { "High Risk": 3017, "Medium Risk": 3, "Low Risk": 8980 },
        feature_importances: [
            { feature: "r_score", importance_pct: 44.18 },
            { feature: "recency_days", importance_pct: 20.12 },
            { feature: "avg_satisfaction_score", importance_pct: 6.74 },
            { feature: "dormancy_ratio", importance_pct: 6.46 },
            { feature: "cancellation_rate", importance_pct: 5.04 },
            { feature: "total_complaints", importance_pct: 3.38 },
            { feature: "direct_channel_ratio", importance_pct: 2.85 },
            { feature: "monetary_spend_eur", importance_pct: 2.14 }
        ],
        members: []
    };
}
