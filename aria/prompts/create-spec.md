# Create Spec Prompt

Create an Aria spec for this task.

Inputs:

- Task request.
- Relevant `aria/context/` files.
- Relevant `aria/review/` files.

Output:

- `requirements.md`, `design.md`, `tasks.md`, and `review.md` using `aria/specs/_template/`.
- Explicit non-goals.
- Validation plan.
- Files that must not be touched.

Do not implement code while creating the spec.
