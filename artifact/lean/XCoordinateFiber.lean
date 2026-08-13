import Mathlib.AlgebraicGeometry.EllipticCurve.Group
import IsogenyCrypto.H7.SignSynchronization

/-!
# H7 elliptic x-coordinate fiber theorem

This file lifts the abstract sign-synchronization theorem to nonsingular points
on an affine Weierstrass curve.

The inner mechanism is the quadratic equation in the `Y`-coordinate. If two
curve points have the same `X`-coordinate, the Weierstrass equation factors so
that their `Y`-coordinates are either equal or related by

`y ↦ -y - a₁x - a₃`,

which is exactly elliptic-curve negation in affine coordinates. Thus the fiber
of the affine `X`-coordinate map is precisely the sign orbit `{P, -P}`. The
point at infinity is represented separately by `none`.

Composing this result with endpoint reconstruction gives an exact fiber theorem
for the ordered map `(R,S) ↦ (x(R), x(S), x(R-S))`: its fibers are precisely the
simultaneous-negation orbits `(R,S) ~ (-R,-S)`.

These theorems are genuine elliptic semantic lifts of
`IsogenyCrypto.H7.signSynchronization`, but they are not yet byte-level decoder
or final-verifier theorems. Canonical field encoding, malformed inputs, role
ordering, exceptional implementation behavior, and auxiliary-isogeny freedom
remain separate obligations.
-/

namespace IsogenyCrypto.H7

open WeierstrassCurve
open WeierstrassCurve.Affine

universe u

variable {F : Type u} [Field F] {W : WeierstrassCurve.Affine F}

/--
The affine `X`-coordinate, with `none` reserved for the point at infinity.

Using `Option F` prevents the point at infinity from being silently identified
with an affine field element.
-/
def xCoordinate : W.Point → Option F
  | .zero => none
  | @WeierstrassCurve.Affine.Point.some _ _ _ x _ _ => some x

@[simp]
theorem xCoordinate_zero : xCoordinate (0 : W.Point) = none :=
  rfl

@[simp]
theorem xCoordinate_some {x y : F} (h : W.Nonsingular x y) :
    xCoordinate (WeierstrassCurve.Affine.Point.some h) = some x :=
  rfl

/-- Negation preserves the affine `X`-coordinate. -/
@[simp]
theorem xCoordinate_neg (P : W.Point) : xCoordinate (-P) = xCoordinate P := by
  cases P <;> rfl

/--
Two nonsingular affine Weierstrass points have the same `X`-coordinate exactly
when they are equal up to one elliptic-curve sign.

The proof does not enumerate field elements. It invokes the structural
quadratic-root theorem `WeierstrassCurve.Affine.Y_eq_of_X_eq`: at a fixed
`X`-coordinate, the only possible `Y`-coordinates are `y` and
`-y - a₁x - a₃`.
-/
theorem xCoordinate_eq_iff_signEquivalent (P Q : W.Point) :
    xCoordinate P = xCoordinate Q ↔ SignEquivalent P Q := by
  constructor
  · intro h
    cases P with
    | zero =>
        cases Q with
        | zero => exact Or.inl rfl
        | @some x₂ y₂ h₂ => cases h
    | @some x₁ y₁ h₁ =>
        cases Q with
        | zero => cases h
        | @some x₂ y₂ h₂ =>
            have hx : x₁ = x₂ := Option.some.inj h
            rcases W.Y_eq_of_X_eq h₁.left h₂.left hx with hy | hy
            · left
              cases hx
              cases hy
              rfl
            · right
              cases hx
              cases hy
              rfl
  · rintro (h | h)
    · simp [h]
    · rw [h, xCoordinate_neg]

/--
The ordered `X`-coordinate classes of `R`, `S`, and `R - S` determine the
ordered pair `(R, S)` up to one common elliptic sign.

This is the composition of two structural facts:

1. each `X`-coordinate fiber is exactly a sign orbit;
2. the reconstruction identities `S = R - (R - S)` and
   `R = (R - S) + S` synchronize the three independently observed signs.
-/
theorem xCoordinateTriple_signSynchronization
    {R S R' S' : W.Point}
    (hR : xCoordinate R' = xCoordinate R)
    (hS : xCoordinate S' = xCoordinate S)
    (hDiff : xCoordinate (R' - S') = xCoordinate (R - S)) :
    (R' = R ∧ S' = S) ∨ (R' = -R ∧ S' = -S) :=
  signSynchronization
    ((xCoordinate_eq_iff_signEquivalent R' R).mp hR)
    ((xCoordinate_eq_iff_signEquivalent S' S).mp hS)
    ((xCoordinate_eq_iff_signEquivalent (R' - S') (R - S)).mp hDiff)

/-- The three ordered x-only observables attached to a pair of points. -/
structure XOnlyTriple (F : Type u) where
  r : Option F
  s : Option F
  diff : Option F

/-- The ordered x-only response map `(R,S) ↦ (x(R),x(S),x(R-S))`. -/
noncomputable def xOnlyTriple (R S : W.Point) : XOnlyTriple F where
  r := xCoordinate R
  s := xCoordinate S
  diff := xCoordinate (R - S)

/--
The fibers of the ordered x-only response map are exactly simultaneous-negation
orbits.

The forward implication is sign synchronization. The reverse implication is
forced by equivariance: simultaneous negation sends `R-S` to `-(R-S)`, and the
x-coordinate is invariant under negation.
-/
theorem xOnlyTriple_eq_iff_globalSign (R S R' S' : W.Point) :
    xOnlyTriple R' S' = xOnlyTriple R S ↔
      (R' = R ∧ S' = S) ∨ (R' = -R ∧ S' = -S) := by
  constructor
  · intro h
    have hR : xCoordinate R' = xCoordinate R :=
      congrArg (fun t : XOnlyTriple F => t.r) h
    have hS : xCoordinate S' = xCoordinate S :=
      congrArg (fun t : XOnlyTriple F => t.s) h
    have hDiff : xCoordinate (R' - S') = xCoordinate (R - S) :=
      congrArg (fun t : XOnlyTriple F => t.diff) h
    exact xCoordinateTriple_signSynchronization hR hS hDiff
  · rintro (⟨rfl, rfl⟩ | ⟨rfl, rfl⟩)
    · rfl
    · have hnegDiff : (-R) - (-S) = -(R - S) := by
        abel
      unfold xOnlyTriple
      rw [xCoordinate_neg R, xCoordinate_neg S, hnegDiff, xCoordinate_neg]

end IsogenyCrypto.H7
