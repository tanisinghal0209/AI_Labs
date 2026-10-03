:- consult('planner.pl').
:- consult('wet_road.pl').

:- begin_tests(existing_prolog_examples).

test(known_connection) :-
    connected(a, b).

test(connection_is_bidirectional) :-
    once(connected(b, a)).

test(can_move_uses_connected_fact) :-
    can_move(a, b).

test(can_move_without_connection_fails, [fail]) :-
    can_move(a, c).

test(missing_connection_fails, [fail]) :-
    connected(a, c).

test(valid_move_uses_connection) :-
    valid_move(b, c).

test(invalid_move_fails, [fail]) :-
    valid_move(a, c).

test(wet_road_is_a_fact) :-
    wet_road.

test(wet_road_is_slippery) :-
    slippery.

test(slippery_road_reduces_speed) :-
    reduce_speed.

:- end_tests(existing_prolog_examples).
