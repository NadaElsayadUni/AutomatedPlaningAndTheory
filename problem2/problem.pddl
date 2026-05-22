(define (problem imv-p02)
  (:domain imv)
  (:objects
    entrance tunnel hallA hallB cryo pod1 pod2 stasis - location
    a1 a2 b1 b2 cs1 cs2 - artifact
    r1 - robot
    slot1 slot2 - slot
  )
  (:init
    (at r1 entrance)
    (robot_slot r1 slot1)
    (robot_slot r1 slot2)
    (slot_free r1 slot1)
    (slot_free r1 slot2)

    (artifact_at a1 hallA)
    (artifact_at a2 hallA)
    (artifact_at b1 hallB)
    (artifact_at b2 hallB)
    (artifact_at cs1 cryo)
    (artifact_at cs2 cryo)

    (connected entrance tunnel)
    (connected tunnel entrance)
    (connected tunnel cryo)
    (connected cryo tunnel)
    (connected tunnel pod1)
    (connected pod1 tunnel)
    (connected tunnel pod2)
    (connected pod2 tunnel)
    (connected tunnel hallA)
    (connected hallA tunnel)
    (connected tunnel hallB)
    (connected hallB tunnel)
    (connected tunnel stasis)
    (connected stasis tunnel)
  )
  (:goal (and
    (artifact_at a1 cryo)
    (artifact_at a2 cryo)
    (artifact_at b1 pod1)
    (artifact_at b2 pod2)
    (artifact_at cs1 stasis)
    (artifact_at cs2 stasis)
  ))
)
