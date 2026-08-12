/-!
# H1 finite-model calibration theorem

This is the single-object algebraic core of the categorical fact that a split
monomorphism is monic.  The Python finite-model oracle mutates away
associativity and searches for a countermodel.  This theorem records exactly
which laws make the cancellation argument go through.

It is a calibration lemma.  It is not yet an encoding of AIM, Forensic
Categories, SQIsign, or their security reductions.
-/

namespace IsogenyCrypto.H1

theorem splitMono_is_leftCancellative
    {α : Type}
    (comp : α → α → α)
    (identity : α)
    (assoc : ∀ x y z, comp (comp x y) z = comp x (comp y z))
    (leftIdentity : ∀ x, comp identity x = x)
    {g f a b : α}
    (leftInverse : comp g f = identity)
    (equalized : comp f a = comp f b) :
    a = b := by
  calc
    a = comp identity a := (leftIdentity a).symm
    _ = comp (comp g f) a := congrArg (fun x => comp x a) leftInverse.symm
    _ = comp g (comp f a) := assoc g f a
    _ = comp g (comp f b) := congrArg (fun x => comp g x) equalized
    _ = comp (comp g f) b := (assoc g f b).symm
    _ = comp identity b := congrArg (fun x => comp x b) leftInverse
    _ = b := leftIdentity b

end IsogenyCrypto.H1

