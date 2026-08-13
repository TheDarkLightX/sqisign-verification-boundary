import Mathlib.Logic.Function.Basic

/-!
# H7 accepted encodings as normalization fixed points

Suppose a byte decoder maps representations into mathematical objects and an
encoder chooses one representation for each object. If verification depends
only on the decoded object, then replacing bytes by

`encode (decode bytes)`

cannot change the verifier verdict, provided decoding the chosen encoding
returns the original object.

The inner ground of canonical accepted encodings is therefore a fixed-point
property: every accepted byte string must already equal its decode-then-encode
normal form. Equivalently, the decoder must be injective on every accepted
fiber.

This theorem separates three obligations that are often conflated:

1. the encoder is a section of the decoder on mathematical objects;
2. verification factors through the decoder;
3. accepted inputs are fixed points of normalization.

It is generic infrastructure. Applying it to SQIsign still requires the exact
production byte type, decoder, encoder, verifier, and authority revision.
-/

namespace IsogenyCrypto.H7

universe u v

variable {Bytes : Type u} {Object : Type v}

/-- Acceptance when a verifier consumes only the decoded mathematical object. -/
def Accepts (decode : Bytes → Object) (verify : Object → Prop) (bytes : Bytes) : Prop :=
  verify (decode bytes)

/-- The representation chosen by re-encoding the decoded object. -/
def normalize (decode : Bytes → Object) (encode : Object → Bytes) (bytes : Bytes) : Bytes :=
  encode (decode bytes)

/-- No two accepted byte strings in one decoder fiber are distinct. -/
def AcceptedFiberInjective
    (decode : Bytes → Object)
    (verify : Object → Prop) : Prop :=
  ∀ ⦃left right : Bytes⦄,
    Accepts decode verify left →
    Accepts decode verify right →
    decode left = decode right →
    left = right

/-- Every accepted representation is already the selected normal form. -/
def AcceptedNormalForm
    (decode : Bytes → Object)
    (encode : Object → Bytes)
    (verify : Object → Prop) : Prop :=
  ∀ ⦃bytes : Bytes⦄,
    Accepts decode verify bytes → normalize decode encode bytes = bytes

/-- Decode-then-encode preserves the decoded object when encoding is a section. -/
theorem decode_normalize
    {decode : Bytes → Object}
    {encode : Object → Bytes}
    (hsection : Function.LeftInverse decode encode)
    (bytes : Bytes) :
    decode (normalize decode encode bytes) = decode bytes :=
  hsection (decode bytes)

/-- A verifier that factors through decoding is invariant under normalization. -/
theorem accepts_normalize_iff
    {decode : Bytes → Object}
    {encode : Object → Bytes}
    {verify : Object → Prop}
    (hsection : Function.LeftInverse decode encode)
    (bytes : Bytes) :
    Accepts decode verify (normalize decode encode bytes) ↔
      Accepts decode verify bytes := by
  unfold Accepts
  rw [decode_normalize hsection]

/--
Accepted-fiber injectivity is equivalent to every accepted encoding being a
normalization fixed point.

Forward: normalization preserves both the decoded object and acceptance, so
fiber injectivity forces the normalized bytes to equal the original bytes.

Backward: two accepted bytes in one decoder fiber have the same normal form;
if each is fixed by normalization, they are equal.
-/
theorem acceptedFiberInjective_iff_acceptedNormalForm
    {decode : Bytes → Object}
    {encode : Object → Bytes}
    {verify : Object → Prop}
    (hsection : Function.LeftInverse decode encode) :
    AcceptedFiberInjective decode verify ↔
      AcceptedNormalForm decode encode verify := by
  constructor
  · intro hinjective bytes haccepted
    apply hinjective
    · exact (accepts_normalize_iff hsection bytes).2 haccepted
    · exact haccepted
    · exact decode_normalize hsection bytes
  · intro hnormal left right hleft hright hdecode
    calc
      left = normalize decode encode left := (hnormal hleft).symm
      _ = normalize decode encode right := by rw [normalize, normalize, hdecode]
      _ = right := hnormal hright

/--
An accepted non-fixed point immediately yields two distinct accepted encodings
of the same decoded object: the original bytes and their normal form.
-/
theorem acceptedCollision_of_not_normalized
    {decode : Bytes → Object}
    {encode : Object → Bytes}
    {verify : Object → Prop}
    (hsection : Function.LeftInverse decode encode)
    {bytes : Bytes}
    (haccepted : Accepts decode verify bytes)
    (hnotFixed : normalize decode encode bytes ≠ bytes) :
    ∃ other : Bytes,
      other ≠ bytes ∧
      Accepts decode verify other ∧
      decode other = decode bytes := by
  refine ⟨normalize decode encode bytes, hnotFixed, ?_, decode_normalize hsection bytes⟩
  exact (accepts_normalize_iff hsection bytes).2 haccepted

end IsogenyCrypto.H7
