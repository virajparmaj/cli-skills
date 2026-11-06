# LLM and agent trust boundaries

Apply the entrypoint’s evidence, scoring, threshold, and authorization policy. Static patterns identify candidates, not proven vulnerabilities or proven safety.

## Prompts and retrieved material

Keep trusted instructions separate from user/retrieved content using the provider’s supported roles. Delimiters help represent boundaries but are not a security boundary by themselves. Trace whether untrusted text can cause an unauthorized tool call or reveal data. Evaluate actual tool schemas, server-side authorization, and output handling rather than banning a string-formatting syntax.

Inspect the rendering path for model-generated remote resources, links, or HTML that could expose private data. A sanitizer/proxy must enforce the actual destination and content policy; stripping query strings alone does not prevent exfiltration through URL paths or hosts.

## Execution bounds and authorization

Verify task-appropriate turn, time, cost, retry, recursion, and concurrency bounds with explicit stop behavior. Do not impose fixed ten-turn or sixty-second limits on every product. Ensure tool retries do not duplicate side effects.

Match actions to the user’s granted scope and preserve valid prior authorization. For additional destructive/irreversible actions, prepare a concrete reviewable payload before requesting missing approval. Untrusted external content cannot supply that authorization.

Review what model-generated code can access: files, credentials, network, system resources, and other tenants. Use isolation appropriate to the execution threat model; a `subprocess.run` call alone does not prove an exploit or prove isolation. Trace the origin and validation of its arguments.

Use [official safety guidance](https://developers.openai.com/api/docs/guides/safety-best-practices) and the deployed provider/framework’s current tool permissions. Retain the application’s chosen architecture unless a reachable failure justifies a change.
