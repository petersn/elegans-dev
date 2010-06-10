Elegans-dev
===========

The original Elegans implementation (see github.com/petersn/elegans) had many problems, but embodied some simple principles:

1. Simple grammars: Elegans used a modified shunting yard parser exclusively.
2. Simple compilers: Elegans had no concept of "if" or "while", those were function calls into the standard library.
3. High level behavior reached simply: Closures and lambdas are trivial in Elegans.

The new Elegans language embodies a new set of principles:

1. Make the obvious solution be high level: Passing lambdas and closures around is good. Continuation passing and tail recursion are natural ways of programming.
2. Static analysis can be quite powerful: Make lambdas, closures, and tail recursion as cheap as other descriptions.
3. Relax the restriction that compilers must provably halt.

