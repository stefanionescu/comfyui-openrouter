# HTTP

Read this rule when you change an HTTP service.

## Requests

- Validate input once where the request enters the service, with a schema. Handlers read the validated value, never the
  raw request.
- Reject unsupported content types on endpoints that take a body. Cap the body size per route, and keep the proxy limit
  equal to the application parser limit.
- Handlers adapt transport to domain calls. They define no validation policy, database access, provider mechanics,
  caching, or business decision.
- Middleware validates, authenticates, rate-limits, and attaches context, and makes no feature decision.

## Responses

- One handler formats error responses. Feature code throws and never builds an HTTP error body.
- The service documents one shape for success and one for errors, and keeps both stable.
- Use precise status codes: 201 for creation, 204 with no body, 4xx for caller errors, and 5xx only for failures the
  caller cannot fix.
- The endpoint or module maps provider and database shapes to responses. Responses name fields for the API, not for
  storage, unless the public interface explicitly exposes the provider format.
- Escape HTML for its rendering context, and never pre-escape JSON field values.

## Sessions and transport

- Terminate TLS at the proxy, and trust forwarding headers only from it.
- When the service issues tokens, a revocation reaches every instance.

## Wire names

- Keep existing protocol header names. A new header carries no `X-` prefix, as
  [Request for Comments (RFC) 6648](https://www.rfc-editor.org/rfc/rfc6648) recommends.

## Operations

- Keep health and readiness endpoints cheap. Call no provider from them.
- Broad rate limits sit at the edge, application limits in middleware, and route limits beside the route.
- Either the proxy or the application compresses responses, not both. Under heavy traffic, the reverse proxy does it.
