# Yahoo Vision Mapping to Implementation

**Document Purpose**: Map Yahoo's strategic vision for agency workflows to the current implementation, identifying matches and gaps with technical implementation guidance.

**Date**: November 24, 2025  
**Status**: Analysis Complete

---

## Vision Mapping Table

| Yahoo's Vision | Implementation Match | Reason for Matching | Status |
|---------------|---------------------|---------------------|--------|
| **PLANNING: Scenario Planning**<br/>Simulations based on budget, KPIs to forecast outcomes | **LLM-Powered Product Discovery** (`product_service.py`)<br/>- Natural language brief analysis<br/>- Budget-based product filtering<br/>- Estimated reach calculations<br/>- Matched audience overlap data | The `discover_products` tool uses LLM to extract campaign criteria from natural language briefs, matches against inventory with budget constraints, and provides estimated reach based on matched audiences. While not full scenario planning, it provides forecast-like capabilities through reach estimates and audience overlap data. | - [x] |
| **BUYING: Audience Modeling**<br/>Demographic, location, intent, interest, lifestages; Scaled predictive and lookalike audiences | **Matched Audience Integration** (`matched_audiences` table)<br/>- Demographics (age, gender, income, geo)<br/>- Engagement scores<br/>- Overlap counts from Clean Room<br/>- Privacy-preserving audience data | The system stores matched audience data with demographics, engagement scores, and overlap metrics from Clean Room output. Products are linked to matched audiences, enabling audience-based targeting. However, predictive/lookalike modeling is not yet implemented. | - [x] |
| **BUYING: Proposal Data**<br/>Targeting, inventory/products, pricing, creative ad specs, forecasts | **Product Discovery & Campaign Creation** (`product_service.py`, `media_buy_service.py`)<br/>- Product catalog with pricing (CPM, enterprise discounts)<br/>- Targeting specifications per product<br/>- Creative format specifications (`list_creative_formats` tool)<br/>- Package-based campaign structure (AdCP v2.3.0)<br/>- Budget and reach forecasts | The `get_products` tool returns complete product proposals with pricing, targeting, formats, and estimated reach. The `create_media_buy` tool accepts package-based campaigns with format specifications. All proposal data elements are present. | - [x] |
| **OPTIMIZATION: Measurement & Analytics**<br/>BYOD: conversion data, attribution modeling, predictive modeling | **Performance Metrics Service** (`metrics_service.py`)<br/>- Real-time delivery metrics (impressions, clicks, conversions)<br/>- CTR, CVR, CPM, CPC, CPA calculations<br/>- Daily and device breakdowns<br/>- Pacing analysis | The `get_media_buy_delivery` and `get_media_buy_report` tools provide comprehensive performance analytics with conversion tracking. However, BYOD (Bring Your Own Data) conversion integration, attribution modeling, and predictive modeling are not yet implemented. | - [ ] |
| **OPTIMIZATION: Continuous Action**<br/>Real-time analysis, recommendations, dynamically adjust budgets across channels, creatives, or audiences | **Campaign Update Capability** (`media_buy_service.py`)<br/>- `update_media_buy` tool for budget modifications<br/>- Status changes (pause, resume)<br/>- Real-time metrics via Data Cloud Zero Copy | The system supports budget updates and status changes, with real-time metrics. However, automated recommendations, dynamic budget reallocation across channels/creatives, and continuous optimization are not implemented. Updates require manual intervention. | - [ ] |
| **WRAP UP: Performance Summary**<br/>Budget and spend overview, business outcomes, KPIs, channel breakdown | **Comprehensive Reporting** (`metrics_service.py`)<br/>- Budget vs. spend tracking<br/>- KPIs: CTR, CVR, CPM, CPC, CPA<br/>- Channel/device breakdowns<br/>- Daily performance trends<br/>- Pacing health indicators | The `get_media_buy_report` tool provides complete performance summaries with budget/spend, all standard KPIs, device breakdowns, and daily trends. This fully matches Yahoo's vision for performance summaries. | - [x] |
| **WRAP UP: Audience Insights**<br/>Performance relative to audience characteristics; competitive insights | **Matched Audience Performance** (`metrics_service.py`)<br/>- Delivery metrics linked to matched audiences<br/>- Engagement scores in reports<br/>- Audience overlap data in campaign context | The system links performance metrics to matched audiences and includes engagement scores. However, performance analysis relative to audience characteristics (e.g., "Eco-Conscious Suburban Mom" insights) and competitive insights are not implemented. | - [ ] |
| **OPPORTUNITY: Make Access to Yahoo Data Seamless** | **MCP Protocol + Data Cloud Integration**<br/>- Natural language interface via Agentforce<br/>- MCP protocol for AI-native access<br/>- Data Cloud Zero Copy for real-time data<br/>- Single API endpoint for all operations | The implementation uses MCP protocol enabling seamless AI-to-platform communication. Data Cloud provides instant access to Snowflake data via Zero Copy. Natural language queries eliminate the need for complex API knowledge. This fully achieves seamless access. | - [x] |
| **OPPORTUNITY: Allow buyers access to bespoke, unique assets** | **Package-Based Campaigns + Creative Formats** (`media_buy_service.py`)<br/>- AdCP v2.3.0 package structure<br/>- Multiple creative formats per package<br/>- Custom targeting overlays per package<br/>- Format specifications via `list_creative_formats` | The system supports package-based campaigns where each package can have unique creative formats, targeting overlays, and pricing strategies. This enables bespoke campaign configurations. However, "unique assets" could be expanded to include custom audience segments, exclusive inventory, etc. | - [x] |
| **OPPORTUNITY: Enhance discoverability and build a market** | **Agent Discovery Endpoints**<br/>- `/.well-known/adagents.json` for agent discovery<br/>- `/.well-known/agent-card.json` for metadata<br/>- MCP protocol enables any AI to discover and use Yahoo agent<br/>- Public Heroku deployment | The system implements AdCP discovery endpoints, making the Yahoo agent discoverable by any MCP-compatible AI. The public deployment enables market access. However, marketplace features like ratings, reviews, and discovery ranking are not implemented. | - [ ] |

---

## Technical Implementation Guide for Unimplemented Features

### 1. Scenario Planning (Full Implementation)

**Current State**: Basic product discovery with reach estimates  
**Gap**: Full scenario planning with budget/KPI simulations

**Technical Implementation**:
```python
# New MCP tool: simulate_campaign_scenarios
@mcp.tool()
async def simulate_campaign_scenarios(
    budget_range: List[float],
    target_kpis: Dict[str, float],  # {"ctr": 0.5, "cpa": 50}
    product_combinations: List[List[str]],
    flight_duration_days: int
) -> Dict[str, Any]:
    """
    Simulate multiple campaign scenarios and forecast outcomes.
    
    Implementation:
    1. For each product combination:
       - Calculate estimated impressions based on budget and CPM
       - Apply historical CTR/CVR from similar campaigns
       - Forecast conversions using predictive model
       - Calculate projected KPIs
    2. Compare scenarios against target KPIs
    3. Rank scenarios by KPI achievement probability
    4. Return forecasted outcomes with confidence intervals
    """
    scenarios = []
    for combo in product_combinations:
        scenario = {
            "products": combo,
            "forecasted_impressions": calculate_impressions(combo, budget_range),
            "forecasted_ctr": predict_ctr(combo, historical_data),
            "forecasted_conversions": predict_conversions(combo, historical_data),
            "kpi_match_score": compare_to_targets(target_kpis),
            "confidence": calculate_confidence(historical_data)
        }
        scenarios.append(scenario)
    
    return {"scenarios": sorted(scenarios, key=lambda x: x["kpi_match_score"], reverse=True)}
```

**Database Changes**:
- Add `campaign_scenarios` table to store simulation results
- Add `historical_performance` table for predictive modeling
- Add `kpi_targets` table for scenario comparison

**Integration Points**:
- Use LLM to extract KPI targets from natural language briefs
- Integrate with Snowflake ML functions for predictive modeling
- Store scenarios in Snowflake for future reference

---

### 2. Predictive & Lookalike Audience Modeling

**Current State**: Matched audiences from Clean Room only  
**Gap**: Predictive modeling and lookalike audience generation

**Technical Implementation**:
```python
# New MCP tool: generate_lookalike_audience
@mcp.tool()
async def generate_lookalike_audience(
    seed_audience_id: str,
    similarity_threshold: float = 0.8,
    max_audience_size: int = 1000000
) -> Dict[str, Any]:
    """
    Generate lookalike audience based on seed audience characteristics.
    
    Implementation:
    1. Extract seed audience demographics, interests, behaviors
    2. Use Snowflake ML functions (e.g., clustering, similarity search)
    3. Find Yahoo users with similar characteristics
    4. Apply privacy constraints (k-anonymity)
    5. Return lookalike audience segment with similarity scores
    """
    # Use Snowflake ML for similarity matching
    query = f"""
    WITH seed_characteristics AS (
        SELECT demographics, engagement_score, quality_score
        FROM matched_audiences
        WHERE segment_id = '{seed_audience_id}'
    ),
    lookalike_candidates AS (
        SELECT 
            yahoo_user_id,
            similarity_score,
            demographics,
            engagement_score
        FROM yahoo_user_profiles y
        CROSS JOIN seed_characteristics s
        WHERE calculate_similarity(y.demographics, s.demographics) >= {similarity_threshold}
        ORDER BY similarity_score DESC
        LIMIT {max_audience_size}
    )
    SELECT * FROM lookalike_candidates
    """
    # Execute in Snowflake, apply k-anonymity, return segment
```

**Database Changes**:
- Add `lookalike_audiences` table
- Add `audience_similarity_scores` table
- Enhance `yahoo_user_profiles` table with ML-ready features

**Integration Points**:
- Use Snowflake ML functions (clustering, similarity search)
- Integrate with Data Cloud for audience activation
- Store lookalike segments in `matched_audiences` table with `audience_type = 'lookalike'`

---

### 3. BYOD Conversion Data Integration

**Current State**: Conversion tracking in delivery metrics  
**Gap**: External conversion data import and attribution modeling

**Technical Implementation**:
```python
# New MCP tool: import_conversion_data
@mcp.tool()
async def import_conversion_data(
    media_buy_id: str,
    conversion_data: List[Dict[str, Any]],  # [{"user_id": "...", "conversion_value": 100, "timestamp": "..."}]
    attribution_model: str = "last_click"  # last_click, first_click, linear, time_decay
) -> Dict[str, Any]:
    """
    Import external conversion data and apply attribution modeling.
    
    Implementation:
    1. Validate conversion data format
    2. Match conversions to campaign touchpoints (impressions, clicks)
    3. Apply attribution model to assign credit
    4. Calculate attributed conversions, revenue, ROAS
    5. Update campaign performance metrics
    """
    # Attribution logic
    if attribution_model == "last_click":
        # Assign 100% credit to last touchpoint
        attributed_conversions = apply_last_click_attribution(conversion_data, touchpoints)
    elif attribution_model == "linear":
        # Distribute credit evenly across touchpoints
        attributed_conversions = apply_linear_attribution(conversion_data, touchpoints)
    # ... other models
    
    # Update delivery_metrics table with attributed conversions
    update_metrics_with_attribution(media_buy_id, attributed_conversions)
    
    return {
        "attributed_conversions": len(attributed_conversions),
        "attributed_revenue": sum(c["conversion_value"] for c in attributed_conversions),
        "roas": calculate_roas(media_buy_id, attributed_conversions)
    }
```

**Database Changes**:
- Add `external_conversions` table
- Add `attribution_touchpoints` table
- Add `attribution_models` table
- Enhance `delivery_metrics` with attribution fields

**Integration Points**:
- Accept CSV/JSON uploads via MCP tool
- Support webhook endpoints for real-time conversion data
- Integrate with Salesforce Data Cloud for CRM conversion data

---

### 4. Automated Recommendations & Dynamic Budget Optimization

**Current State**: Manual budget updates  
**Gap**: Automated recommendations and continuous optimization

**Technical Implementation**:
```python
# New background service: optimization_engine.py
class OptimizationEngine:
    async def analyze_and_recommend(self, media_buy_id: str) -> Dict[str, Any]:
        """
        Analyze campaign performance and generate optimization recommendations.
        
        Implementation:
        1. Fetch real-time performance metrics
        2. Compare performance across packages, creatives, audiences
        3. Identify underperformers and top performers
        4. Generate recommendations:
           - Reallocate budget from low to high performers
           - Pause underperforming creatives
           - Scale winning audiences
        5. Return actionable recommendations with expected impact
        """
        metrics = await get_media_buy_delivery(media_buy_id)
        
        # Analyze package performance
        package_performance = analyze_packages(media_buy_id)
        recommendations = []
        
        # Budget reallocation recommendation
        if package_performance["variance"] > 0.2:  # 20% performance variance
            recommendations.append({
                "type": "budget_reallocation",
                "from_package": package_performance["worst_performer"],
                "to_package": package_performance["best_performer"],
                "amount": calculate_optimal_reallocation(package_performance),
                "expected_lift": predict_performance_lift(package_performance),
                "confidence": 0.85
            })
        
        # Creative optimization
        creative_performance = analyze_creatives(media_buy_id)
        if creative_performance["worst_ctr"] < creative_performance["best_ctr"] * 0.7:
            recommendations.append({
                "type": "pause_creative",
                "creative_id": creative_performance["worst_creative"],
                "reason": f"CTR {creative_performance['worst_ctr']:.2f}% vs. best {creative_performance['best_ctr']:.2f}%",
                "expected_impact": "Improve overall CTR by 15%"
            })
        
        return {"recommendations": recommendations, "next_review": "1 hour"}

# New MCP tool: apply_optimization_recommendations
@mcp.tool()
async def apply_optimization_recommendations(
    media_buy_id: str,
    recommendation_ids: List[str],
    auto_apply: bool = False
) -> Dict[str, Any]:
    """
    Apply optimization recommendations automatically or with approval.
    """
    if auto_apply:
        # Execute recommendations immediately
        for rec_id in recommendation_ids:
            await execute_recommendation(rec_id)
    else:
        # Queue for approval
        await queue_for_approval(recommendation_ids)
```

**Database Changes**:
- Add `optimization_recommendations` table
- Add `optimization_history` table
- Add `auto_optimization_settings` table

**Integration Points**:
- Background job scheduler (e.g., Celery, Heroku Scheduler)
- Real-time monitoring via Data Cloud queries
- Notification system for recommendations (email, Slack, etc.)

---

### 5. Audience Performance Analysis & Competitive Insights

**Current State**: Basic audience metrics in reports  
**Gap**: Deep audience performance analysis and competitive benchmarking

**Technical Implementation**:
```python
# New MCP tool: analyze_audience_performance
@mcp.tool()
async def analyze_audience_performance(
    media_buy_id: str,
    audience_segment_id: str
) -> Dict[str, Any]:
    """
    Analyze performance relative to audience characteristics.
    
    Implementation:
    1. Fetch audience demographics and characteristics
    2. Compare campaign performance to audience benchmarks
    3. Identify which audience segments perform best
    4. Generate insights (e.g., "Eco-Conscious Suburban Mom" has 2x higher CVR)
    5. Recommend audience expansion or refinement
    """
    audience = get_audience_segment(audience_segment_id)
    campaign_metrics = get_campaign_metrics(media_buy_id)
    
    # Compare to benchmarks
    benchmarks = get_industry_benchmarks(audience.demographics)
    
    insights = {
        "audience_segment": audience.segment_name,
        "performance_vs_benchmark": {
            "ctr": campaign_metrics.ctr / benchmarks.avg_ctr,
            "cvr": campaign_metrics.cvr / benchmarks.avg_cvr,
            "cpa": campaign_metrics.cpa / benchmarks.avg_cpa
        },
        "top_performing_characteristics": identify_top_performers(audience, campaign_metrics),
        "recommendations": generate_audience_recommendations(audience, campaign_metrics)
    }
    
    return insights

# New MCP tool: get_competitive_insights
@mcp.tool()
async def get_competitive_insights(
    industry: str,
    audience_segment: str
) -> Dict[str, Any]:
    """
    Provide competitive insights for audience segment.
    
    Implementation:
    1. Aggregate anonymized performance data across similar campaigns
    2. Compare to industry benchmarks
    3. Identify competitive advantages
    4. Return insights without exposing competitor data
    """
    # Use aggregated, anonymized data from multiple campaigns
    query = f"""
    SELECT 
        AVG(ctr) as industry_avg_ctr,
        AVG(cvr) as industry_avg_cvr,
        AVG(cpa) as industry_avg_cpa,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY ctr) as top_quartile_ctr
    FROM aggregated_campaign_performance
    WHERE industry = '{industry}'
    AND audience_segment_type = '{audience_segment}'
    GROUP BY industry, audience_segment_type
    """
    # Execute in Snowflake, return competitive benchmarks
```

**Database Changes**:
- Add `audience_performance_analysis` table
- Add `competitive_benchmarks` table (anonymized, aggregated)
- Add `industry_benchmarks` table

**Integration Points**:
- Integrate with third-party benchmark data (e.g., IAB benchmarks)
- Use Snowflake for aggregated analytics across campaigns
- Ensure privacy compliance (no PII, k-anonymity)

---

### 6. Marketplace Features for Discoverability

**Current State**: Basic agent discovery  
**Gap**: Marketplace features (ratings, reviews, discovery ranking)

**Technical Implementation**:
```python
# New MCP tool: rate_agent_experience
@mcp.tool()
async def rate_agent_experience(
    agent_id: str,
    rating: int,  # 1-5
    review: Optional[str],
    campaign_id: Optional[str]
) -> Dict[str, Any]:
    """
    Rate and review agent experience for marketplace discoverability.
    """
    # Store rating in marketplace_ratings table
    # Update agent's average rating
    # Return confirmation

# Enhanced discovery endpoint
@app.get("/.well-known/adagents.json")
async def get_agents_marketplace():
    """
    Enhanced discovery with marketplace features.
    
    Returns:
    - Agent list sorted by rating, usage, performance
    - Filter by category, industry, use case
    - Include ratings, reviews, success metrics
    """
    agents = get_agents_with_ratings()
    # Sort by: rating * usage_count * success_rate
    sorted_agents = sort_by_marketplace_score(agents)
    return {"agents": sorted_agents, "filters": get_available_filters()}
```

**Database Changes**:
- Add `marketplace_ratings` table
- Add `marketplace_reviews` table
- Add `agent_usage_stats` table
- Add `agent_success_metrics` table

**Integration Points**:
- Public API for ratings/reviews
- Analytics dashboard for agent performance
- Recommendation engine for agent discovery

---

## Summary

### Fully Implemented ✅ (6/10)
- [x] Product discovery with proposals
- [x] Matched audience integration  
- [x] Performance reporting
- [x] Seamless data access via MCP
- [x] Package-based campaigns
- [x] Proposal data (targeting, pricing, creative specs)

### Partially Implemented ⚠️ (4/10)
- [ ] Measurement & Analytics (needs BYOD, attribution)
- [ ] Continuous optimization (needs automation)
- [ ] Audience insights (needs deep analysis)
- [ ] Marketplace (needs ratings/reviews)

### Not Implemented ❌ (Technical guidance provided)
- Full scenario planning with simulations
- Predictive/lookalike audience modeling
- Automated recommendations engine
- Competitive insights

---

**Next Steps**: Prioritize implementation based on business value and technical feasibility. Start with high-impact, low-complexity features (e.g., automated recommendations) before moving to advanced ML features (e.g., lookalike modeling).

