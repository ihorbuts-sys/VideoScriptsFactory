# Hand pose references

The three verdict palm gestures were approved by the owner and are preserved. Cup and fork grips use their own poses; facing the camera is not a validity requirement for a hand holding an object.

- [Moleskine: Tea Teatime](https://mymoleskine.moleskine.com/msk_app/templates/MSK_Tea_EN_A4_Teatime.pdf): an illustrated cup-and-saucer grip with the thumb above the handle, a bent index finger and supporting fingers below. This is the reference chosen for this cup, not a claim that every cup must be held identically.
- [Emily Post: Top Table Manners](https://emilypost.substack.com/p/etiquette-today-top-table-manners-ff7): a utensil held between thumb and index, with the middle finger supporting it and the handle resting toward the thumb/index web. This informs the fork's tripod-style grip rather than a full-fist vertical hold.
- [Proko: Muscle Anatomy of the Hand](https://www.proko.com/course-lesson/how-to-draw-hands-muscle-anatomy-of-the-hand/): anatomical hand forms and the distinct thumb mass. The thumb requires its own opposition pose, not the same curl as the four fingers.
- [Kenhub: Pronation and Supination](https://www.kenhub.com/en/library/anatomy/pronation-and-supination): forearm rotation positions the hand. The rig shares axial rotation through the shoulder and forearm instead of twisting only the wrist.

Implementation checks use the actual canonical left-hand skeleton and evaluated geometry. Finger flexion follows the measured palm side of the source hand; the index/thumb side stays above the pinky side; cup thumb tips stay above the bent index. The original skinned model is not mirrored to imitate an opposite hand. Front-camera mirroring happens only on the final preview image.
