# Zero-knowledge review procedure

Use with pack Z (`references/invariant-packs.md`) whenever a proof system, circuit, zkVM or privacy protocol is in scope.

## 1. Statement table

One row per proof the system uses.

| ID | Relation in words | Relation formally | Public inputs | Private witness | Prover | Verifier (where it runs) | What the application concludes on acceptance |

A proof whose statement cannot be written down precisely is a finding.

## 2. Stack inventory

Proof system and variant; arithmetisation; polynomial commitment scheme; curve and field; hash functions; DSL or framework and compiler version; circuit libraries and versions; setup type and ceremony; verifier implementation(s); recursion, aggregation or folding scheme. Feed every item into the Phase 0B component lookup.

## 3. Specification-to-circuit trace

- Map every clause of the specification to the constraints that enforce it (give constraint groups IDs: F1.C1, F1.C2 ...).
- Mark every signal as constrained or assigned-only.
- A specification clause with no constraint, a signal that is assigned but never constrained, and a constraint nobody can explain are each findings.

## 4. Per-statement interrogation

Answer each from code and documents; unresolved items become questions.

1. Soundness: can any witness that is not a valid one satisfy the constraints? Which values are computed outside the circuit and only hinted in?
2. Completeness: can every honest input be proved? Any over-constraint that could freeze funds or exits?
3. Zero knowledge: what do the proof and public inputs reveal? Is blinding present where the scheme needs it?
4. Is the statement proved the statement needed? Do public inputs bind chain, contract, nullifier, recipient, amount and epoch?
5. Field arithmetic: range and bit-length checks, overflow and aliasing, non-native field emulation, division and inverse edge cases.
6. Determinism: can the prover choose between several valid witnesses with different meaning (for example two nullifiers for one note)?
7. Fiat-Shamir: does the transcript absorb every public input, the statement and all prior messages, with domain separation?
8. Setup: who ran it, how many participants, what must be trusted, where do the parameters come from, can they be swapped?
9. Parameters: what security level results, and does it rest on proven or conjectured soundness?
10. Verifier: on-curve and subgroup checks, public-input encoding and range, malleability, verification-key binding, who can upgrade it?
11. Recursion and aggregation: is the inner verification fully constrained, and are deferred checks discharged?
12. zkVM or zkEVM: do instruction, memory, lookup and precompile constraints match the specified machine?
13. Application layer: double-spend and linkability protection, Merkle-root freshness, proof replay across contexts, front-running of proofs by relayers.
14. Toolchain: known compiler or framework bugs, optimiser behaviour, audit status of dependencies.

## 5. Known-bug sweep

Compare the circuits against the current categories in the 0xPARC ZK Bug Tracker and the Phase 0B results for the framework in use. Baseline categories: under-constrained circuits, non-deterministic circuits, arithmetic overflow and underflow, mismatched bit lengths, unused public inputs optimised out, weak Fiat-Shamir, trusted-setup leak, assigned but not constrained.

## 6. Protocol-level simulation

Model the surrounding protocol in Phase 4, treating proof verification as a check on (statement, public inputs). Test: proof replay, public-input substitution, nullifier reuse, stale Merkle roots, verifier-key swap, relayer front-running.

## 7. Verification plan and residual risk

Recommend, after confirming currency in Phase 0B: static analysis and under-constraint detection, fuzzing and prover/verifier differential testing, formal verification of critical circuits, independent circuit audit. State plainly that a clean tool run is not a soundness proof, and that a design review of a proof system does not replace a circuit audit.
