# OttoShell manifesto

Manifesto for OttoShell.

## we're doing AI wrong

Modern AI systems are largely built on opaque layers and cumbersome abstractions that distract from the clarity of text-based interactions. By emphasizing direct CLI communication, we harness the natural text → text paradigm that language models excel at. Our approach bypasses unnecessary intermediaries, enabling bespoke tools with clear, precise operation.

## MCP breaks the cardinal rule

[MCP](https://modelcontextprotocol.io) shows how overcomplicated protocols can dilute clarity. By embedding unnecessary layers of abstraction, MCP strays from the direct interactions essential for transparency. In contrast, our design champions a text-centric client/server model that resonates with the simplicity of Unix.

## the Unix philosophy

The [Unix philosophy](https://en.wikipedia.org/wiki/Unix_philosophy) champions doing one thing well using small, composable tools and plain text for communication. This foundational ethos guides our approach: each tool is designed to perform a specific function, ensuring every operation remains predictable, modifiable, and efficient.

## tricks for speed

The [logit bias trick](https://github.com/dkdc-io/stringflow/blob/main/src/stringflow/main.py#L110-L173) demonstrates how constraining the decision space at key moments can markedly improve performance. We apply similar strategies to narrow command search spaces, reducing computational overhead and accelerating CLI response times—speed is a necessity for effective text-based AI engagement.

## tricks for UX

Our system strikes a balance between shell and AI by merging their strengths into a seamless experience. To illustrate the tradeoffs we manage, consider the following approaches:

- use a shell with an indicator for executing AI tasks
- use AI with an indicator for handling shell operations

¿por qué no los dos?

By blending the intuitive nature of the CLI with the adaptive reasoning of AI, we enable users to transition fluidly between precise command-line operations and expansive natural language processing. This integration creates an experience that is both accessible and powerful—why choose one when you can have both?

## learnings from codai, dkdc, and Ibis Birdbrain

Our experiments have underscored several key insights:

- figuring out whether to run a process in a shell or via AI is trivial (and deterministic)
- still, commands that narrow the search space are essential for efficiency
- use logit bias trick for speed

These learnings confirm that combining clear, text-based command structures with smart, adaptive shortcuts is the way forward for bespoke AI tools. By integrating proven Unix principles with modern innovation, we continue to redefine efficient client/server interactions in the AI domain.
