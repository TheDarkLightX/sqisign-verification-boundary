import IsogenyCrypto.H7.CanonicalNormalization
import IsogenyCrypto.H7.XCoordinateFiber

/-!
# H7 x-only observables as a diagonal-sign quotient

The ordered observable

`(R, S) ↦ (x(R), x(S), x(R - S))`

does not identify the two signs independently.  Its exact fibers are the
orbits of the diagonal involution `(R, S) ↦ (-R, -S)`.  Consequently it is a
complete invariant for the quotient of `E × E` by simultaneous negation.

This file makes that quotient statement explicit and then isolates the extra
condition needed to lift mathematical-object uniqueness to byte uniqueness.
Equal decoded x-only observations force one diagonal-sign orbit, but equal
bytes follow only when every accepted byte string is the selected normal form
of that orbit.

The inner mechanism is a two-stage factorization:

1. `xOnlyTriple` is injective after quotienting by its exact fibers;
2. an orbit-invariant canonicalizer followed by an encoder collapses each
   accepted orbit to one byte string.

No production decoder, SQIsign verifier, or security notion is instantiated
here.  Those remain refinement obligations.
-/

namespace IsogenyCrypto.H7

open WeierstrassCurve

universe u v

variable {F : Type u} [Field F] {W : WeierstrassCurve.Affine F}

/-- A pair of elliptic-curve points carrying the diagonal sign action. -/
abbrev PointPair (W : WeierstrassCurve.Affine F) := W.Point × W.Point

/-- Two point pairs differ by at most one simultaneous elliptic sign. -/
def PairSignEquivalent (left right : PointPair W) : Prop :=
  (left.1 = right.1 ∧ left.2 = right.2) ∨
    (left.1 = -right.1 ∧ left.2 = -right.2)

/-- The ordered x-only observable attached to a point pair. -/
noncomputable def pairXOnly (pair : PointPair W) : XOnlyTriple F :=
  xOnlyTriple pair.1 pair.2

/-- Equality of ordered x-only observations is exactly simultaneous sign. -/
theorem pairXOnly_eq_iff_pairSignEquivalent (left right : PointPair W) :
    pairXOnly left = pairXOnly right ↔ PairSignEquivalent left right := by
  simpa [pairXOnly, PairSignEquivalent] using
    (xOnlyTriple_eq_iff_globalSign (W := W)
      right.1 right.2 left.1 left.2)

/-- The kernel setoid of the ordered x-only observable. -/
noncomputable def xOnlySetoid : Setoid (PointPair W) where
  r left right := pairXOnly left = pairXOnly right
  iseqv := {
    refl := fun _ => rfl
    symm := fun h => h.symm
    trans := fun h₁ h₂ => h₁.trans h₂
  }

/-- The kernel relation is the diagonal elliptic-sign orbit relation. -/
theorem xOnlySetoid_rel_iff_pairSignEquivalent (left right : PointPair W) :
    (xOnlySetoid (W := W)).r left right ↔ PairSignEquivalent left right :=
  pairXOnly_eq_iff_pairSignEquivalent left right

/-- The x-only observable induced on its quotient. -/
noncomputable def xOnlyQuotientMap :
    Quotient (xOnlySetoid (W := W)) → XOnlyTriple F :=
  Quotient.lift pairXOnly (by
    intro left right h
    exact h)

@[simp]
theorem xOnlyQuotientMap_mk (pair : PointPair W) :
    xOnlyQuotientMap (W := W) (Quotient.mk _ pair) = pairXOnly pair :=
  rfl

/--
The ordered x-only triple is a complete invariant of the simultaneous-sign
quotient: the induced quotient map is injective.
-/
theorem xOnlyQuotientMap_injective :
    Function.Injective (xOnlyQuotientMap (W := W)) := by
  intro left right
  refine Quotient.inductionOn₂ left right ?_
  intro leftPair rightPair h
  exact Quotient.sound h

variable {Bytes : Type v}

/-- A partial byte decoder followed by the mathematical x-only observable. -/
noncomputable def decodedXOnly
    (decode : Bytes → Option (PointPair W)) (bytes : Bytes) :
    Option (XOnlyTriple F) :=
  (decode bytes).map pairXOnly

/--
When two byte strings successfully decode, equality of their x-only
observations is exactly simultaneous sign of the decoded pairs.
-/
theorem decodedXOnly_eq_iff_pairSignEquivalent
    {decode : Bytes → Option (PointPair W)}
    {left right : Bytes} {leftPair rightPair : PointPair W}
    (hleft : decode left = some leftPair)
    (hright : decode right = some rightPair) :
    decodedXOnly decode left = decodedXOnly decode right ↔
      PairSignEquivalent leftPair rightPair := by
  simpa [decodedXOnly, hleft, hright] using
    (pairXOnly_eq_iff_pairSignEquivalent leftPair rightPair)

/-- A canonicalizer is constant on every simultaneous-sign orbit. -/
def OrbitInvariant (canonicalize : PointPair W → PointPair W) : Prop :=
  ∀ ⦃left right : PointPair W⦄,
    PairSignEquivalent left right → canonicalize left = canonicalize right

/--
Every accepted byte string is the selected encoding of the sign orbit of its
successfully decoded pair.
-/
def AcceptedOrbitNormalForm
    (decode : Bytes → Option (PointPair W))
    (encode : PointPair W → Bytes)
    (canonicalize : PointPair W → PointPair W)
    (accepted : Bytes → Prop) : Prop :=
  ∀ ⦃bytes : Bytes⦄ ⦃pair : PointPair W⦄,
    accepted bytes →
    decode bytes = some pair →
    encode (canonicalize pair) = bytes

/--
Byte uniqueness factors into two independent facts:

1. equal decoded x-only observations put the mathematical pairs in one
   simultaneous-sign orbit;
2. accepted-orbit normalization assigns that orbit one byte string.

Canonicality is therefore not needed for object-level sign synchronization,
but it is exactly the additional bridge needed for byte-level uniqueness.
-/
theorem acceptedBytes_eq_of_decodedXOnly_eq
    {decode : Bytes → Option (PointPair W)}
    {encode : PointPair W → Bytes}
    {canonicalize : PointPair W → PointPair W}
    {accepted : Bytes → Prop}
    (hinvariant : OrbitInvariant canonicalize)
    (hnormal : AcceptedOrbitNormalForm decode encode canonicalize accepted)
    {left right : Bytes} {leftPair rightPair : PointPair W}
    (hleftAccepted : accepted left)
    (hrightAccepted : accepted right)
    (hleftDecode : decode left = some leftPair)
    (hrightDecode : decode right = some rightPair)
    (hobserved : decodedXOnly decode left = decodedXOnly decode right) :
    left = right := by
  have hsign : PairSignEquivalent leftPair rightPair :=
    (decodedXOnly_eq_iff_pairSignEquivalent hleftDecode hrightDecode).mp
      hobserved
  calc
    left = encode (canonicalize leftPair) :=
      (hnormal hleftAccepted hleftDecode).symm
    _ = encode (canonicalize rightPair) := by rw [hinvariant hsign]
    _ = right := hnormal hrightAccepted hrightDecode

/-- No two accepted, successfully decoded byte strings share one x-only fiber. -/
def AcceptedXOnlyFiberInjective
    (decode : Bytes → Option (PointPair W))
    (accepted : Bytes → Prop) : Prop :=
  ∀ ⦃left right : Bytes⦄ ⦃leftPair rightPair : PointPair W⦄,
    accepted left →
    accepted right →
    decode left = some leftPair →
    decode right = some rightPair →
    decodedXOnly decode left = decodedXOnly decode right →
    left = right

/--
Re-encoding the canonical representative of any accepted decoded pair remains
accepted and decodes to the same simultaneous-sign orbit.

This is the precise section/refinement premise needed for the converse
direction below.  It is deliberately weaker than demanding that the
re-encoded byte string decode to the identical point-pair representative.
-/
def AcceptedCanonicalEncodingRefinement
    (decode : Bytes → Option (PointPair W))
    (encode : PointPair W → Bytes)
    (canonicalize : PointPair W → PointPair W)
    (accepted : Bytes → Prop) : Prop :=
  ∀ ⦃bytes : Bytes⦄ ⦃pair : PointPair W⦄,
    accepted bytes →
    decode bytes = some pair →
    accepted (encode (canonicalize pair)) ∧
      ∃ decodedPair : PointPair W,
        decode (encode (canonicalize pair)) = some decodedPair ∧
          PairSignEquivalent decodedPair pair

/--
Under an orbit-invariant canonicalizer and a section/refinement law for its
encoding, accepted x-only-fiber injectivity is *equivalent* to accepted bytes
being orbit normal forms.

The forward implication normalizes one accepted byte string and invokes fiber
injectivity inside the same decoded sign orbit.  The reverse implication is
`acceptedBytes_eq_of_decodedXOnly_eq`.  This equivalence identifies the exact
serialization obligation once the mathematical quotient theorem and the
canonical-encoding refinement premise have been fixed.
-/
theorem acceptedXOnlyFiberInjective_iff_acceptedOrbitNormalForm
    {decode : Bytes → Option (PointPair W)}
    {encode : PointPair W → Bytes}
    {canonicalize : PointPair W → PointPair W}
    {accepted : Bytes → Prop}
    (hinvariant : OrbitInvariant canonicalize)
    (hrefines :
      AcceptedCanonicalEncodingRefinement
        decode encode canonicalize accepted) :
    AcceptedXOnlyFiberInjective decode accepted ↔
      AcceptedOrbitNormalForm decode encode canonicalize accepted := by
  constructor
  · intro hinjective bytes pair haccepted hdecode
    rcases hrefines haccepted hdecode with
      ⟨hnormalAccepted, decodedNormal, hnormalDecode, hnormalSign⟩
    apply hinjective hnormalAccepted haccepted hnormalDecode hdecode
    exact
      (decodedXOnly_eq_iff_pairSignEquivalent
        hnormalDecode hdecode).2 hnormalSign
  · intro hnormal left right leftPair rightPair
      hleftAccepted hrightAccepted hleftDecode hrightDecode hobserved
    exact acceptedBytes_eq_of_decodedXOnly_eq
      hinvariant hnormal
      hleftAccepted hrightAccepted hleftDecode hrightDecode hobserved

end IsogenyCrypto.H7
