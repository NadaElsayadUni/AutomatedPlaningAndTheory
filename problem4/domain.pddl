(define (domain imv)
  (:requirements :strips :typing :durative-actions :equality)
  (:types location artifact robot slot vunit)
  (:predicates
    (at ?r - robot ?l - location)
    (artifact_at ?a - artifact ?l - location)
    (slot_free ?r - robot ?s - slot)
    (in_slot ?a - artifact ?r - robot ?s - slot)
    (robot_slot ?r - robot ?s - slot)
    (connected ?from ?to - location)
    (manip_free ?r - robot)
    (tunnel ?l - location)
    (non_tunnel ?l - location)
    (sealing_on ?u - vunit)
    (sealing_off ?u - vunit)
  )

  (:durative-action move
    :parameters (?r - robot ?from ?to - location)
    :duration (= ?duration 2)
    :condition (and
      (at start (at ?r ?from))
      (at start (connected ?from ?to))
      (at start (non_tunnel ?from))
      (at start (non_tunnel ?to))
      (at start (manip_free ?r))
    )
    :effect (and
      (at start (not (manip_free ?r)))
      (at end (not (at ?r ?from)))
      (at end (at ?r ?to))
      (at end (manip_free ?r))
    )
  )

  (:durative-action move_into_tunnel
    :parameters (?r - robot ?from ?to - location ?u - vunit)
    :duration (= ?duration 3)
    :condition (and
      (at start (at ?r ?from))
      (at start (connected ?from ?to))
      (at start (tunnel ?to))
      (at start (non_tunnel ?from))
      (at start (sealing_on ?u))
      (at start (manip_free ?r))
    )
    :effect (and
      (at start (not (manip_free ?r)))
      (at end (not (at ?r ?from)))
      (at end (at ?r ?to))
      (at end (manip_free ?r))
    )
  )

  (:durative-action move_out_of_tunnel
    :parameters (?r - robot ?from ?to - location ?u - vunit)
    :duration (= ?duration 3)
    :condition (and
      (at start (at ?r ?from))
      (at start (connected ?from ?to))
      (at start (tunnel ?from))
      (at start (non_tunnel ?to))
      (at start (sealing_on ?u))
      (at start (manip_free ?r))
    )
    :effect (and
      (at start (not (manip_free ?r)))
      (at end (not (at ?r ?from)))
      (at end (at ?r ?to))
      (at end (manip_free ?r))
    )
  )

  (:durative-action activate_sealing
    :parameters (?r - robot ?l - location ?u - vunit)
    :duration (= ?duration 1)
    :condition (and
      (at start (at ?r ?l))
      (at start (non_tunnel ?l))
      (at start (sealing_off ?u))
      (at start (manip_free ?r))
    )
    :effect (and
      (at start (not (manip_free ?r)))
      (at end (sealing_on ?u))
      (at end (not (sealing_off ?u)))
      (at end (manip_free ?r))
    )
  )

  (:durative-action deactivate_sealing
    :parameters (?r - robot ?l - location ?u - vunit)
    :duration (= ?duration 1)
    :condition (and
      (at start (at ?r ?l))
      (at start (non_tunnel ?l))
      (at start (sealing_on ?u))
      (at start (manip_free ?r))
    )
    :effect (and
      (at start (not (manip_free ?r)))
      (at end (not (sealing_on ?u)))
      (at end (sealing_off ?u))
      (at end (manip_free ?r))
    )
  )

  (:durative-action load
    :parameters (?r - robot ?a - artifact ?l - location ?s - slot ?u - vunit)
    :duration (= ?duration 1)
    :condition (and
      (at start (at ?r ?l))
      (at start (artifact_at ?a ?l))
      (at start (slot_free ?r ?s))
      (at start (robot_slot ?r ?s))
      (at start (manip_free ?r))
      (at start (non_tunnel ?l))
      (at start (sealing_off ?u))
    )
    :effect (and
      (at start (not (manip_free ?r)))
      (at end (not (slot_free ?r ?s)))
      (at end (in_slot ?a ?r ?s))
      (at end (not (artifact_at ?a ?l)))
      (at end (manip_free ?r))
    )
  )

  (:durative-action unload
    :parameters (?r - robot ?a - artifact ?l - location ?s - slot ?u - vunit)
    :duration (= ?duration 1)
    :condition (and
      (at start (at ?r ?l))
      (at start (in_slot ?a ?r ?s))
      (at start (manip_free ?r))
      (at start (non_tunnel ?l))
      (at start (sealing_off ?u))
    )
    :effect (and
      (at start (not (manip_free ?r)))
      (at end (slot_free ?r ?s))
      (at end (not (in_slot ?a ?r ?s)))
      (at end (artifact_at ?a ?l))
      (at end (manip_free ?r))
    )
  )
)
