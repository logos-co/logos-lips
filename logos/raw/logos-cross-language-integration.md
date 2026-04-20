---
title: LOGOS-CROSS-LANGUAGE-INTEGRATION
name: Logos Cross-Language Integration
status: raw
category: Standards Track
tags: logos-core, ffi, javascript, nodejs, nim, event-pumping, sdk
editor: Logos Core Team
contributors:
- Filip Dimitrijevic <filip@status.im>
---

## Abstract

This RFC documents the cross-language integration capabilities of the Logos Core Platform as specified in the current implementation. The platform provides experimental support for JavaScript/Node.js integration through core library calls, event pumping patterns via Qt Remote Objects, and SDK components that enable external applications to interact with the modular runtime system.

## Background / Rationale / Motivation

The Logos Core Platform is built on a modular, process-isolated architecture using a Remote Procedure Call (RPC) mechanism for inter-process communication. To enable broader ecosystem adoption, the platform provides experimental cross-language integration capabilities that allow external applications to interact with the core modules.

Key motivations include:

- **External Application Integration**: Enable JavaScript/Node.js applications to interact with Logos modules
- **Process Isolation Maintenance**: Preserve security boundaries while enabling cross-language access
- **Simplified Development**: Provide higher-level APIs that abstract inter-process communication complexity
- **Event-Driven Integration**: Support asynchronous, event-based communication patterns

## Theory / Semantics

### Cross-Language Architecture Overview

The cross-language integration system is built on a Remote Procedure Call (RPC) mechanism using Qt Remote Objects infrastructure, providing experimental APIs for external language runtimes to interact with Logos modules.

```text
┌─────────────────────────────────────────────────────────────────┐
│              External Applications (Node.js/Electron)          │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼ (Core Library Calls)
┌─────────────────────────────────────────────────────────────────┐
│                    Core API Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  • logos_core_call_plugin_method_async()                       │
│  • logos_core_register_event_listener()                        │
│  • Authentication token management                             │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 RPC Mechanism Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  • Remote method invocation (up to 5 arguments)                │
│  • Return types: void, bool, int, QString, QVariant, etc.      │
│  • Event subscription and publishing                           │
│  • Local inter-process socket communication                    │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Process-Isolated Modules                          │
├─────────────────────────────────────────────────────────────────┤
│  Modules running in separate processes with authentication     │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Patterns

Based on the current implementation:

#### 1. Core Library Integration

External applications make calls through core library functions:

- Experimental API for NodeJS/Electron applications
- Abstracts inter-process communication complexity
- Maintains process isolation boundaries

#### 2. Event-Based Communication

Asynchronous event handling through callbacks:

- Event subscription via callback mechanisms
- Results delivered through signals/callbacks
- ModuleProxy validates authentication tokens

## JavaScript/Node.js Integration Specification

### Core API Functions

Based on the specifications, the platform provides experimental APIs for NodeJS/Electron integration:

#### Available Core Functions

- `logos_core_call_plugin_method_async()` - Asynchronous method calls to modules
- `logos_core_register_event_listener()` - Event subscription and callback registration

#### Method Call Limitations

The RPC mechanism supports:

- **Up to 5 arguments** per method call
- **Return types**: void, bool, int, QString, QVariant, QJsonArray, QStringList
- **Asynchronous execution** with callback-based result delivery

#### Authentication Requirements

All external applications must:

- Provide valid authentication tokens for module access
- Use the existing TokenManager system for token handling
- Authenticate through the ModuleProxy validation layer

## Event Pumping Patterns for External Runtimes

### Event Subscription System

The platform provides event-driven communication through the RPC mechanism with callback-based event handling.

#### Event Registration

External applications can:

- **Subscribe to module events** using callback mechanisms
- **Attach event listeners** with optional callback functions
- **Receive event notifications** routed through the RPC mechanism

#### Asynchronous Operation

As specified in the documentation:

> "The SDK is asynchronous: calls return immediately and results are delivered via callbacks/signals."

#### Event Routing

- Events are routed through the RPC mechanism
- Authentication tokens are validated before method calls
- Callback functions handle event processing in external runtimes

## SDK Implementation Details

### Core SDK Components

Based on the specifications, the platform provides several key SDK components:

#### LogosAPI Classes

- **LogosAPI** - Main API interface
- **LogosAPIClient** - Client-side implementation
- **LogosAPIProvider** - Provider-side implementation

#### Core Functionality

The SDK provides:

- **Connection management** - Abstracts inter-process communication connections
- **Token handling** - Integrates with TokenManager for authentication
- **Asynchronous invocation** - Supports async method calls with callbacks

#### C++ SDK Integration

The platform uses:

- **C++ SDK** that wraps complex inter-process communication details
- **Cross-module communication** via local inter-process sockets
- **Authentication integration** via token-based system

### TokenManager Integration

As specified:

- Handles authentication tokens between modules
- Provides thread-safe token storage and validation
- Provides authentication between modules

## Security/Privacy Considerations

### Authentication and Authorization

- **Token-based Authentication**: All cross-language interactions must authenticate using the existing token-based authentication system
- **Process Isolation**: Each module runs in a separate process for security and robustness
- **Authentication Integration**: Uses ModuleProxy for token validation before method calls

## Implementation Suggestions

### Development Approach

- **Common Interface**: Modules must implement a common interface for cross-language compatibility
- **SDK Usage**: Use the C++ SDK which wraps complex inter-process communication details
- **Asynchronous Patterns**: Leverage the asynchronous nature of the RPC mechanism
- **Process Isolation**: Design modules to operate independently in separate processes

## Future Enhancements

As noted in the specifications, this is a "living document" that may not fully reflect the ultimate design. Potential areas for development:

- **Expanded Language Support**: Beyond the current experimental NodeJS/Electron integration
- **Enhanced SDK Features**: Further abstraction of inter-process communication complexity
- **Stabilization**: Moving experimental features to stable status

## References

### Normative

- [Logos Core Architecture RFC](./logos-core-architecture.md)
- [Logos Authentication and Capability System RFC](./logos-authentication-capability-system.md)
- [Logos Core Proof of Concept - Specifications](https://github.com/logos-co/logos-core-poc/blob/develop/docs/specs.md)

### Informative

- [Qt Remote Objects Documentation](https://doc.qt.io/qt-6/qtremoteobjects-index.html)
- [C++ SDK Documentation](https://github.com/logos-co/logos-core-poc)

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
