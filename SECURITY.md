# Security Policy

## Scope

LSP D-PLANNER is a client-side web application. It has no backend, no API, no user accounts, and stores nothing remotely. All computation runs in the browser.

## Reporting a safety issue in the algorithm

If you find a calculation error that could produce an unsafe dive plan:

1. Open a GitHub Issue with the label `algorithm-bug`
2. Include: depth, BT, gas mix, GF settings, and what LSP produces vs what you expect
3. Reference the software you used for comparison (Multideco, Subsurface, etc.)

Algorithm bugs are taken seriously. This is dive planning software.

## Reporting a security vulnerability

If you find an XSS, injection, or other browser security issue, open a GitHub Issue. Since there is no server or user data, the attack surface is limited to the browser environment.

## What this software is not

This is not certified medical or safety-critical software. It is a planning aid. See README.md disclaimer.
