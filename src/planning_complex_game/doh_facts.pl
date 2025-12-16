% ============================================================
% strategy_map_data.pl
%
% Data-only facts used by rule prologs. No rules here.
% Intended usage:
%   :- consult('strategy_map_data.pl').
%   % or
%   :- ['strategy_map_data.pl'].
% ============================================================

% -------------------------
% Status levels / ordering
% -------------------------
% Order matches your legend top-to-bottom:
%   Broken (black), Major Pain, Pain, Warning (Minor Pain), OK
status_level(broken,     1, black,   'Broken').
status_level(major_pain, 2, maroon,  'Major Pain').
status_level(pain,       3, orange,  'Pain').
status_level(warning,    4, yellow,  'Minor Pain / Warning').
status_level(ok,         5, green,   'OK').

% -------------------------
% Node registry
% -------------------------
% node(NodeId, NodeType, HumanName).
% NodeType: goal | kpi | config
node(g0, goal,   'Visit Conversion Rate').
node(g1, goal,   'Page Load Time').
node(g2, goal,   'Cost').

node(k1, kpi,    'Marketing Spend').
node(k2, kpi,    'Site Volume').
node(k3, kpi,    'Site Visits').
node(k4, kpi,    'Clicks/Sales Ratio').
node(k5, kpi,    'Blog Clicks').
node(k6, kpi,    'Visit Bounce').
node(k7, kpi,    'Product Clicks').
node(k8, kpi,    'Customer Satisfaction').

node(c1, config, 'Increase Ad Spend').
node(c2, config, 'Improve SEO').
node(c3, config, 'Drip Email').
node(c4, config, 'Add Product Recommendation').
node(c5, config, 'On Page Product Bundles').
node(c6, config, 'Upgrade Hosting').
node(c7, config, 'AI Customer Service').

% -------------------------
% KPI / Goal measurements
% -------------------------
% metric(NodeId, Value, Unit, AsOfDate).
% Units are illustrative; use whatever you standardize on.
% Dates in ISO so you can sort; format however you like.
metric(g0, 0.012, ratio,     '2025-12-16').   % 1.2% conversion
metric(g1, 0.95,  seconds,   '2025-12-16').   % 0.95s load time
metric(g2, 4200,  usd_month, '2025-12-16').   % monthly operating cost

metric(k1, 1800,  usd_month, '2025-12-16').
metric(k2, 65000, visits_mo, '2025-12-16').
metric(k3, 52000, visits_mo, '2025-12-16').
metric(k4, 42.0,  clicks_per_sale, '2025-12-16').
metric(k5, 12000, clicks_mo, '2025-12-16').
metric(k6, 0.62,  ratio,     '2025-12-16').   % 62% bounce
metric(k7, 9000,  clicks_mo, '2025-12-16').
metric(k8, 3.9,   stars_5,   '2025-12-16').

% -------------------------
% Targets / desired ranges
% -------------------------
% target(NodeId, TargetValue, Unit, Notes).
target(g0, 0.020, ratio,   'Target conversion rate (2.0%).').
target(g1, 0.90,  seconds, 'Target load time under 0.90s.').
target(g2, 4500,  usd_month,'Budget ceiling; some pain tolerated.').

target(k6, 0.50, ratio, 'Bounce ideally 50% or lower.').
target(k8, 4.3,  stars_5, 'Customer satisfaction target.').

% -------------------------
% Pain bands
% -------------------------
% This is the “rules for pain levels” as pure data.
% band(NodeId, Level, LowerBound, UpperBound, BoundType).
%
% BoundType:
%   higher_is_worse  -> larger numbers mean more pain (e.g., cost, bounce, load time, clicks/sale)
%   lower_is_worse   -> smaller numbers mean more pain (e.g., conversion rate, satisfaction, visits)
%
% Interpretation (common pattern):
%   - Bands are inclusive on the lower edge, exclusive on upper edge
%   - broken is the “worst” band
%
% ---- Goals ----
band(g0, broken,     0.000, 0.005, lower_is_worse).
band(g0, major_pain, 0.005, 0.010, lower_is_worse).
band(g0, pain,       0.010, 0.015, lower_is_worse).
band(g0, warning,    0.015, 0.020, lower_is_worse).
band(g0, ok,         0.020, 1.000, lower_is_worse).

band(g1, ok,         0.000, 1.000, higher_is_worse).   % <= 1.0s
band(g1, warning,    1.000, 1.300, higher_is_worse).
band(g1, pain,       1.300, 1.800, higher_is_worse).
band(g1, major_pain, 1.800, 3.000, higher_is_worse).
band(g1, broken,     3.000, 999.0, higher_is_worse).

band(g2, ok,         0,    4500,  higher_is_worse).
band(g2, warning,    4500, 6000,  higher_is_worse).
band(g2, pain,       6000, 8000,  higher_is_worse).
band(g2, major_pain, 8000, 12000, higher_is_worse).
band(g2, broken,     12000, 999999, higher_is_worse).

% ---- KPIs ----
band(k1, ok,         0,    2500,  higher_is_worse).
band(k1, warning,    2500, 3500,  higher_is_worse).
band(k1, pain,       3500, 5000,  higher_is_worse).
band(k1, major_pain, 5000, 8000,  higher_is_worse).
band(k1, broken,     8000, 999999, higher_is_worse).

band(k2, broken,     0,     15000, lower_is_worse).
band(k2, major_pain, 15000, 30000, lower_is_worse).
band(k2, pain,       30000, 45000, lower_is_worse).
band(k2, warning,    45000, 60000, lower_is_worse).
band(k2, ok,         60000, 999999, lower_is_worse).

band(k3, broken,     0,     12000, lower_is_worse).
band(k3, major_pain, 12000, 25000, lower_is_worse).
band(k3, pain,       25000, 38000, lower_is_worse).
band(k3, warning,    38000, 50000, lower_is_worse).
band(k3, ok,         50000, 999999, lower_is_worse).

band(k4, ok,         0.0,  25.0,  higher_is_worse).
band(k4, warning,    25.0, 40.0,  higher_is_worse).
band(k4, pain,       40.0, 60.0,  higher_is_worse).
band(k4, major_pain, 60.0, 90.0,  higher_is_worse).
band(k4, broken,     90.0, 999.0, higher_is_worse).

band(k5, broken,     0,     1500,  lower_is_worse).
band(k5, major_pain, 1500,  4000,  lower_is_worse).
band(k5, pain,       4000,  8000,  lower_is_worse).
band(k5, warning,    8000,  11000, lower_is_worse).
band(k5, ok,         11000, 999999, lower_is_worse).

band(k6, ok,         0.00, 0.45, higher_is_worse).
band(k6, warning,    0.45, 0.55, higher_is_worse).
band(k6, pain,       0.55, 0.65, higher_is_worse).
band(k6, major_pain, 0.65, 0.80, higher_is_worse).
band(k6, broken,     0.80, 1.01, higher_is_worse).

band(k7, broken,     0,    1000,  lower_is_worse).
band(k7, major_pain, 1000, 3500,  lower_is_worse).
band(k7, pain,       3500, 6500,  lower_is_worse).
band(k7, warning,    6500, 8500,  lower_is_worse).
band(k7, ok,         8500, 999999, lower_is_worse).

band(k8, broken,     0.0,  2.5, lower_is_worse).
band(k8, major_pain, 2.5,  3.3, lower_is_worse).
band(k8, pain,       3.3,  3.9, lower_is_worse).
band(k8, warning,    3.9,  4.2, lower_is_worse).
band(k8, ok,         4.2,  5.1, lower_is_worse).

% -------------------------
% Config ranges and current/test settings
% -------------------------
% config_bounds(ConfigId, Min, Max, Unit).
% config_state(ConfigId, Current, Test, Unit).
%
% The unit can be:
%   - percentage_implemented (0..1)
%   - dollars
%   - tier (0..N)
%   - boolean (0/1)
config_bounds(c1, 0, 5000, usd_month).
config_state(c1, 1800, 2500, usd_month).

config_bounds(c2, 0.0, 1.0, percentage_implemented).
config_state(c2, 0.3, 0.6, percentage_implemented).

config_bounds(c3, 0.0, 1.0, percentage_implemented).
config_state(c3, 0.2, 0.5, percentage_implemented).

config_bounds(c4, 0.0, 1.0, percentage_implemented).
config_state(c4, 0.0, 0.8, percentage_implemented).

config_bounds(c5, 0.0, 1.0, percentage_implemented).
config_state(c5, 0.0, 0.7, percentage_implemented).

config_bounds(c6, 0, 3, tier).      % e.g., 0=none, 1=basic, 2=better, 3=best
config_state(c6, 1, 2, tier).

config_bounds(c7, 0.0, 1.0, percentage_implemented).
config_state(c7, 0.1, 0.6, percentage_implemented).

% Optional: some configs are “projects in a box”
% config_is_project(ConfigId, true/false).
config_is_project(c2, true).  % Improve SEO is a project, not just a knob
config_is_project(c6, true).  % Hosting upgrade is a project
config_is_project(c7, true).  % AI CS is a project
config_is_project(c4, true).  % Recommendations can be a project
config_is_project(c5, true).  % Bundles can be a project
config_is_project(c1, false). % Spend is closer to a knob
config_is_project(c3, true).  % Drip campaigns often act like a project

% -------------------------
% Relationship facts (optional, but usually worth having)
% -------------------------
% link(FromId, ToId, Kind, Polarity, Strength, LineStyle, Label).
%
% Kind:
%   pro | con | correlation
% Polarity:
%   positive | negative
% LineStyle:
%   solid | dash
%
% Strength is 0..1 and can be your “0.70 means 0.30 unknown” style confidence.
%
% Keep only what you want the planners/rules to see.
link(c1, k1, pro,         positive, 0.95, solid, 'increases').
link(c2, k3, pro,         positive, 0.70, solid, 'increases').
link(c3, k3, pro,         positive, 0.55, solid, 'increases').
link(c4, k7, pro,         positive, 0.60, solid, 'increases').
link(c5, k7, pro,         positive, 0.65, solid, 'increases').

link(k3, k2, correlation, positive, 0.80, solid, 'drives').
link(k2, g1, correlation, negative, 0.60, dash,  'pressure_on_latency'). % volume can hurt load time

link(c6, g1, pro,         positive, 0.70, solid, 'improves').
link(c6, g2, con,         positive, 0.75, solid, 'increases_cost').

link(k7, g0, correlation, positive, 0.65, solid, 'supports_conversion').
link(k6, g0, correlation, negative, 0.80, solid, 'hurts_conversion').

link(c7, k8, pro,         positive, 0.55, dash,  'can_improve').
link(c7, g2, con,         positive, 0.45, dash,  'can_increase_cost').

% -------------------------
% Pain tolerance knobs (planner constraints)
% -------------------------
% max_allowed_level(NodeId, Level).
% Example: "we can afford a little more pain on cost"
max_allowed_level(g2, pain).        % cost allowed up to "pain" temporarily
max_allowed_level(g1, warning).     % page load time must not exceed warning
max_allowed_level(g0, warning).     % conversion must not drop below warning

% For KPIs, you can also constrain:
max_allowed_level(k8, warning).     % satisfaction shouldn’t drop too far
max_allowed_level(k6, pain).        % bounce can rise temporarily, but not to major pain

% -------------------------
% Notes / provenance (optional)
% -------------------------
% provenance(FactGroup, Source, Notes).
provenance(bands, 'initial_guess', 'Replace thresholds with learned/validated bands from TCW/TM distributions.').
provenance(links, 'diagram',       'Strength is confidence, not causality. Adjust as you learn more.').
