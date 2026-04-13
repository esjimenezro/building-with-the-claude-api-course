# STREAMING SERVICE CHURN ANALYSIS REPORT

## Executive Summary
This analysis examines customer churn patterns in a streaming service dataset containing 500 customers with a **38.6% overall churn rate** (193 churned, 307 retained).

## Major Churn Drivers Identified

### 1. **Low Engagement Metrics** (Most Critical)
- **Total Viewing Hours**: Churned customers watch **16.6 hours less** per month (66.6 vs 83.2 hours)
- **Effect Size**: Medium (Cohen's d = -0.521) - statistically significant (p < 0.001)
- **Session Duration**: Churned customers have **shorter average sessions** (53.4 vs 64.1 minutes)
- **Unique Titles**: Churned customers watch **fewer unique titles** (17.0 vs 22.1 titles)

### 2. **Customer Service Issues** (Strong Predictor)
- **High CS Interactions**: Strong positive correlation with churn (Cohen's d = 0.596)
- Customers with **4+ service interactions** show significantly higher churn rates
- This suggests dissatisfaction that leads to multiple support contacts

### 3. **Subscription Tier Impact**
- **Basic Tier**: Highest churn rate at **43.5%**
- **Standard Tier**: Moderate churn rate at **39.5%**
- **Premium Tier**: Lowest churn rate at **24.1%**
- Basic subscribers are **1.8x more likely** to churn than Premium subscribers

### 4. **Content Preference Patterns**
- **Horror** genre viewers: Highest churn (52.3%)
- **Thriller** genre viewers: Second highest (48.3%)
- **Documentary** genre viewers: Lowest churn (25.9%)
- **Comedy** viewers: Relatively low churn (33.0%)

### 5. **Pricing Sensitivity**
- Churned customers have **slightly lower monthly costs** ($11.18 vs $12.11)
- Small but statistically significant effect (p = 0.005)
- Suggests value perception issues rather than price sensitivity

## Machine Learning Feature Importance Rankings
1. **Total Viewing Hours** (24.0% importance) - Primary predictor
2. **Average Session Duration** (19.4% importance) - Engagement quality
3. **Number of Unique Titles** (17.6% importance) - Content exploration
4. **Top Genre** (11.1% importance) - Content preference impact
5. **Binge Watching Sessions** (10.9% importance) - Viewing pattern
6. **Customer Service Interactions** (9.1% importance) - Satisfaction indicator
7. **Monthly Cost** (4.3% importance) - Price factor
8. **Subscription Tier** (3.7% importance) - Service level

## Statistical Significance
All major predictors show **highly significant differences** (p < 0.001):
- Total viewing hours, binge sessions, unique titles, session duration, and CS interactions all demonstrate clear statistical separation between churned and retained customers.

## Key Insights & Recommendations

### Immediate Actions (High Impact)
1. **Engagement Monitoring**: Flag customers with <50 viewing hours/month for retention campaigns
2. **Customer Service Excellence**: Proactively address customers with 3+ service interactions
3. **Basic Tier Retention**: Develop specific retention strategies for Basic subscribers
4. **Content Strategy**: Reduce reliance on Horror/Thriller content, promote Documentary content

### Medium-Term Strategies
1. **Personalized Recommendations**: Improve content discovery to increase unique titles watched
2. **Session Quality**: Focus on increasing average session duration through better UX
3. **Premium Upselling**: Leverage the 43% lower churn rate in Premium tier
4. **Predictive Analytics**: Implement real-time churn prediction using the identified drivers

### Content & Product Insights
1. **Genre Strategy**: Documentary and Comedy content shows better retention
2. **Binge-Watching**: Encourage healthy binge-watching patterns (8+ sessions/month)
3. **Value Communication**: Address value perception issues, especially for Basic tier

## Risk Segmentation
- **High Risk**: Basic subscribers, <60 viewing hours, 3+ CS interactions, Horror/Thriller preference
- **Medium Risk**: Standard tier, 60-80 viewing hours, 1-2 CS interactions
- **Low Risk**: Premium subscribers, >100 viewing hours, Documentary/Comedy preference, minimal CS contact

This analysis provides a data-driven foundation for targeted retention strategies and customer experience improvements.