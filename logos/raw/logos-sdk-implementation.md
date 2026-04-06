---
title: LOGOS-SDK-IMPLEMENTATION
name: Logos Core SDK Implementation
status: raw
category: Standards Track
tags: logos-core, sdk, api, qt-remote-objects, thread-safety
editor: Logos Core Team
contributors:
- Filip Dimitrijevic <filip@status.im>
---

## Abstract

This RFC documents the C++ SDK implementation for the Logos Core Platform as specified in the current architectural documentation. The SDK provides abstractions over Qt Remote Objects to enable module development in the process-isolated architecture, featuring LogosAPIProvider/Client/Consumer components and thread-safe TokenManager integration.

## Background / Rationale / Motivation

The Logos Core Platform requires a C++ SDK to support the modular, process-isolated architecture. According to the documented architecture, the SDK addresses the need for:

- **Abstraction over Qt Remote Objects**: Simplify inter-module communication for developers
- **Authentication Integration**: Handle security transparently within the SDK
- **Developer-Friendly Interfaces**: Provide easy-to-use APIs for module development
- **Cross-Language Support**: Enable bindings for multiple programming languages

## SDK Architecture Overview

### Component Structure

According to the documented architecture:

> "The C++ SDK provides abstractions over Qt Remote Objects"

The documentation describes a provider/client separation:

> "Provider/Client Separation
>
> - **LogosAPIProvider**: Exposes module's interface via `ModuleProxy` on `local:logos_<moduleName>`
> - **LogosAPIClient**: Connects to other modules and invokes their methods via `LogosAPIConsumer`
> - **ModuleProxy**: Validates tokens and dispatches calls to actual module implementation
> - **TokenManager**: Thread-safe storage and validation of authentication tokens"

### LogosAPI Entry Point

The documentation describes LogosAPI as:

> "LogosAPI (Entry Point)
>
> - Single instance per module
> - Encapsulates a provider and a cache of clients
> - Provides access to clients for calling other modules
> - Handles token storage and retrieval through TokenManager"

## LogosAPIProvider Component

### Provider Role

According to the specifications:

> "**LogosAPIProvider**: Exposes module's interface via `ModuleProxy` on `local:logos_<moduleName>`"

The provider is responsible for exposing the module's interface through the Qt Remote Objects registry system.

## LogosAPIClient Component

### Client Role

The documentation states:

> "**LogosAPIClient**: Connects to other modules and invokes their methods via `LogosAPIConsumer`"

The client component handles connections to other modules and method invocation.

## LogosAPIConsumer Component

### Consumer Role

The documentation references LogosAPIConsumer as part of the client architecture:

> "Connects to other modules and invokes their methods via `LogosAPIConsumer`"

The consumer appears to handle the actual remote object interaction, though specific implementation details are not provided in the current documentation.

## Qt Remote Objects Integration

### Communication Mechanism

The platform uses Qt Remote Objects for inter-process communication as documented:

> "Communication uses Qt Remote Objects over local sockets:
>
> - **Registry-based discovery**: Modules register objects in `QRemoteObjectRegistryHost`
> - **Asynchronous method calls**: Non-blocking invocation with callbacks
> - **Event propagation**: Modules can subscribe to events from other modules
> - **Automatic marshalling**: Qt handles serialization of method parameters and return values"

### Registry-Based Discovery

The system uses registry-based discovery where:

> "Modules register objects in `QRemoteObjectRegistryHost`"

This enables modules to discover and connect to available services.

### Platform Dependencies

As documented:

> "Platform built on Qt Remote Objects for IPC"
>
> "`QRemoteObjectRegistryHost` has no built-in security mechanisms"

## TokenManager Implementation and Thread Safety

### Thread Safety

According to the authentication documentation:

> "Each module maintains a thread-safe TokenManager for storing authentication tokens"

### Responsibilities

The documented responsibilities include:

> "Thread-safe storage and validation of authentication tokens"

### Developer Transparency

The documentation indicates:

> "Token management is handled internally and transparent to developers"

This means the SDK handles authentication automatically without requiring manual token management from module developers.

## Integration with Authentication System

### Automatic Security Handling

The documentation describes automatic security integration:

> "ModuleProxy validates tokens and dispatches calls to actual module implementation"

### Authentication Requirements

The system enforces authentication as documented:

> "Authentication is required for all remote calls"

The SDK integrates with the authentication system transparently.

## Current Implementation Status

### Proof of Concept State

According to the documentation:

> "**Current State**: Proof of Concept
>
> - Core architecture functional with process isolation
> - Authentication system working with token validation
> - C++ SDK available for module development
> - Example modules operational (Waku, Chat, IRC, Wallet)"

### Known Limitations

The documentation identifies areas for improvement:

> "API Improvements Needed
>
> Current `LogosAPI` shaped by authentication development. Potential improvements:
>
> - Modules only need `LogosAPIClient`, not full `LogosAPI`
> - Simplified event triggering: `logosAPI->trigger("eventName", data)`
> - Simplified event listening: `logosAPI->onEvent("module", "event", callback)`
> - Merge duplicate token methods (`informModuleToken` vs `informModuleToken_module`)"

## Language Bindings

### Multi-Language Support

The documentation indicates support for multiple languages:

> "**Multi-Language Support**:
>
> - **C++**: Native SDK with full Qt integration
> - **JavaScript**: FFI bindings with event pumping via `logos_core_process_events()`
> - **Nim**: Wrapper over C API
> - **Future**: Any language with Qt bindings or FFI support"

### Current Status

> "Experimental JavaScript and Nim bindings available"

## Performance Considerations

### Process Overhead

The documentation acknowledges:

> "Each module spawns separate process with memory overhead"

### Asynchronous Design

The system uses asynchronous patterns:

> "**Asynchronous method calls**: Non-blocking invocation with callbacks"

## Future Enhancements

While not specified in the current documentation, the identified API improvements suggest potential areas for enhancement in SDK design and usability.

## Conclusion

The Logos Core SDK Implementation, as documented in the current specifications, provides essential abstractions for module development in the process-isolated architecture. The SDK successfully demonstrates:

- **Provider/Client/Consumer architecture** for clean separation of concerns
- **Qt Remote Objects integration** with registry-based discovery and asynchronous communication
- **Thread-safe TokenManager integration** for transparent authentication handling
- **Cross-language binding support** for diverse development environments

This SDK foundation enables module developers to focus on application logic while the platform handles the complexity of process isolation, authentication, and inter-module communication.

## References

- [Logos Core Architecture RFC](./logos-core-architecture.md)
- [Logos Core Authentication and Capability System RFC](./logos-authentication-capability-system.md)
- [Qt Remote Objects Documentation](https://doc.qt.io/qt-6/qtremoteobjects-index.html)

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
