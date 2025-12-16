% ============================================================
% kpi_pain_site_clicks.pl
%
% Pain-level rules for "site clicks" KPIs, using strategy_map_data.pl
% (i.e., band/5 + metric/4).
%
% Usage:
%   :- consult('strategy_map_data.pl').
%   :- consult('kpi_pain_site_clicks.pl').
%
% Examples:
%   ?- site_clicks_status(k5, Level).
%   ?- site_clicks_status(k7, Level).
%   ?- site_clicks_summary(S).
% ============================================================

:- consult('strategy_map_data.pl').

% -------------------------
% Which KPIs count as "site clicks" in your diagram
% -------------------------
site_clicks_kpi(k5).  % Blog Clicks
site_clicks_kpi(k7).  % Product Clicks

% -------------------------
% Generic status evaluation from facts
% -------------------------
% status(NodeId, Level) is true if NodeId's current metric value falls into
% the band(NodeId, Level, Low, High, ...) range.
status(NodeId, Level) :-
    metric(NodeId, Value, _Unit, _AsOf),
    band(NodeId, Level, Low, High, _BoundType),
    Value >= Low,
    Value <  High,
    !.

% If no band matched (missing data), fall back to "broken" as a conservative default.
status(NodeId, broken) :-
    metric(NodeId, _Value, _Unit, _AsOf),
    \+ band(NodeId, _AnyLevel, _Low, _High, _BoundType),
    !.

% -------------------------
% Site clicks: KPI -> pain level
% -------------------------
site_clicks_status(KpiId, Level) :-
    site_clicks_kpi(KpiId),
    status(KpiId, Level).

% Convenience: icon + label (uses your status_level/4 facts)
site_clicks_status_ui(KpiId, Icon, Label) :-
    site_clicks_status(KpiId, Level),
    status_icon(Level, Icon),
    status_level(Level, _Order, _ColorName, Label).

% -------------------------
% Icons (match your blog legend)
% -------------------------
status_icon(broken,     '⬛').
status_icon(major_pain, '🟥').
status_icon(pain,       '🟧').
status_icon(warning,    '🟨').
status_icon(ok,         '🟩').

% -------------------------
% Quick summary (returns a list of terms you can print/log)
% -------------------------
site_clicks_summary(Summary) :-
    findall(
        site_click(KpiId, Name, Value, Unit, Level, Icon),
        (
            site_clicks_kpi(KpiId),
            node(KpiId, kpi, Name),
            metric(KpiId, Value, Unit, _AsOf),
            site_clicks_status(KpiId, Level),
            status_icon(Level, Icon)
        ),
        Summary
    ).
