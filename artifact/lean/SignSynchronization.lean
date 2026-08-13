import Mathlib.Algebra.Group.Basic
import Mathlib.Tactic

/-!
# H7 structural sign-synchronization theorem

The x-only response triple remembers the sign classes of `R`, `S`, and
`R - S`.  The subtraction relation forces the first two signs to synchronize.

This statement is stronger than the rank-two `ZMod (2^f)` formulation: it
holds in every additive commutative group, with no freeness, basis, exponent,
or non-2-torsion assumption.  At 2-torsion, the two global signs simply
represent the same element.

This theorem concerns the intermediate ordered triple only.  It says nothing
about auxiliary-isogeny freedom, final-verifier fibers, serialization, or
strong unforgeability.
-/

namespace IsogenyCrypto.H7

/-- Equality after forgetting the sign of an additive-group element. -/
def SignEquivalent {A : Type*} [Neg A] (x y : A) : Prop :=
  x = y ∨ x = -y

@[refl]
theorem signEquivalent_refl {A : Type*} [Neg A] (x : A) :
    SignEquivalent x x :=
  Or.inl rfl

/--
The ordered sign classes of `R`, `S`, and `R - S` determine `(R, S)` up to
one common sign.

The inner mechanism is reconstruction: `S = R - (R - S)` and
`R = (R - S) + S`.  Whichever sign is fixed by the difference reconstructs
the other point with the same sign.
-/
theorem signSynchronization
    {A : Type*} [AddCommGroup A]
    {R S R' S' : A}
    (hR : SignEquivalent R' R)
    (hS : SignEquivalent S' S)
    (hDiff : SignEquivalent (R' - S') (R - S)) :
    (R' = R ∧ S' = S) ∨ (R' = -R ∧ S' = -S) := by
  rcases hR with hR | hR
  · rcases hS with hS | hS
    · exact Or.inl ⟨hR, hS⟩
    · rcases hDiff with hDiff | hDiff
      · exact Or.inl ⟨hR, by
          calc
            S' = R' - (R' - S') := by abel
            _ = R - (R - S) := by rw [hDiff, hR]
            _ = S := by abel⟩
      · exact Or.inr ⟨by
          calc
            R' = (R' - S') + S' := by abel
            _ = -(R - S) + (-S) := by rw [hDiff, hS]
            _ = -R := by abel, hS⟩
  · rcases hS with hS | hS
    · rcases hDiff with hDiff | hDiff
      · exact Or.inl ⟨by
          calc
            R' = (R' - S') + S' := by abel
            _ = (R - S) + S := by rw [hDiff, hS]
            _ = R := by abel, hS⟩
      · exact Or.inr ⟨hR, by
          calc
            S' = R' - (R' - S') := by abel
            _ = (-R) - (-(R - S)) := by rw [hDiff, hR]
            _ = -S := by abel⟩
    · exact Or.inr ⟨hR, hS⟩

end IsogenyCrypto.H7
