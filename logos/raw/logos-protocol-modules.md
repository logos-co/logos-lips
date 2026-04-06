---
title: LOGOS-PROTOCOL-MODULES
name: Logos Protocol Modules
status: raw
category: Standards Track
tags: logos-core, protocol-modules, waku, chat, irc, wallet
editor: Logos Core Team
contributors:
- Filip Dimitrijevic <filip@status.im>
---

## Abstract

This RFC documents the protocol modules within the Logos Core Platform as specified in the current implementation. It covers the verified module implementations including Waku, Chat, IRC, and Wallet modules that operate within the platform's process-isolated modular architecture.

## Background / Rationale / Motivation

The Logos Core Platform supports various protocol modules that enable decentralized application functionality. These modules implement specific protocols and services while leveraging the platform's modular architecture benefits:

- **Protocol Integration**: Each module implements a specific protocol or service
- **Process Isolation**: Modules run in separate processes for fault tolerance
- **Inter-Module Communication**: Modules can interact through the platform's RPC mechanism
- **Extensibility**: New protocol modules can be added to extend platform capabilities

This RFC documents the protocol modules as they exist in the current proof-of-concept implementation.

## Protocol Module Architecture

### Common Module Structure

All protocol modules in the platform follow the same architectural patterns:

- **Process Isolation**: Each module runs in its own process
- **Common Interface**: Modules implement a common interface for platform integration
- **LogosAPI Integration**: Modules use LogosAPI for inter-module communication
- **Authentication**: Modules participate in the platform's token-based authentication system

### Module Communication Patterns

Protocol modules can:

- **Expose Methods**: Other modules can call methods on protocol modules
- **Emit Events**: Protocol modules can publish events for other modules to receive
- **Subscribe to Events**: Protocol modules can listen for events from other modules
- **Method Introspection**: The platform supports discovering available methods on modules

## Chat Module

### Documented Functionality

Based on the specifications, the Chat module provides:

#### Available Methods

- `joinChannel` - As shown in the specifications example
- `sendMessage` - As shown in the specifications example

#### Event Handling

- **Event Emission**: Chat module can emit `chatMessage` events (as documented in example)
- **Event Subscription**: Other modules can subscribe to chat events (as shown in specifications)

### Example Usage

As documented in the specifications:

```cpp
// Example event handling for chat messages
logosAPI->getClient("chat")->onEvent(chatObject, this, "chatMessage",
    [this](const QString &eventName, const QVariantList &data) {
        // Handle chat message event
        // Event data contains message details
    });
```

## Waku Module

### Module Status

The Waku module is listed among the "Various Modules that can be loaded by the Core" in the specifications. Specific implementation details are not provided in the current documentation.

### Integration Context

- **Module Status**: Listed as loadable by the Core in the specifications
- **Implementation Details**: Not provided in the current documentation

## IRC Module

### Module Reference

The IRC module is referenced as "Logos IRC" in the specifications. Detailed implementation patterns are not documented in the current specifications.

### Platform Integration

- **Module Reference**: Referenced as "Logos IRC" in the specifications
- **Implementation Details**: Not documented in the current specifications

## Wallet Module

### Documented Capabilities

Based on the specifications:

- **Method Introspection**: The Wallet module supports method discovery
- **Platform Integration**: Operates within the modular architecture
- **Authentication Integration**: Participates in the platform's authentication system

### Implementation Context

Specific blockchain integration details are not elaborated in the current specifications. The module follows the standard platform patterns for process isolation and inter-module communication.

## Module Integration Patterns

### Authentication and Authorization

All protocol modules:

- **Token Authentication**: Use the platform's token-based authentication system
- **Capability Requests**: Must request access to other modules through the Capability Module
- **Process Boundaries**: Benefit from operating system-level security isolation

### Communication Framework

Protocol modules communicate through:

- **RPC Mechanism**: Remote Procedure Call system for method invocation
- **Event System**: Asynchronous event publishing and subscription
- **LogosAPI**: Unified API for inter-module communication
- **Authentication Tokens**: Secure communication between modules

### Platform Services

Based on the specifications, protocol modules integrate with:

- **LogosAPI**: For inter-module communication
- **Authentication System**: Token-based authentication as documented
- **RPC Mechanism**: For method calls between modules
- **Event System**: For event publishing and subscription

## Security/Privacy Considerations

### Process Isolation

- **Separate Processes**: Each module runs in its own process as documented in the specifications
- **Process Benefits**: Process isolation provides fault tolerance and security boundaries

### Security Requirements

- **Token Authentication**: Uses the platform's token-based authentication system as documented
- **Process Isolation**: Each module runs in a separate process as specified

## Implementation Considerations

### Module Requirements

Based on the specifications:

- **Common Interface**: Modules implement a common interface (specific details not provided in current specs)
- **Process Isolation**: Each module runs in its own process as documented
- **LogosAPI Integration**: Modules use LogosAPI for inter-module communication
- **Authentication**: Modules participate in the platform's token-based authentication system

## Future Enhancements

As noted in the specifications, this is a "living document" that may not fully reflect the ultimate design. Current areas for potential development:

- **Enhanced Protocol Support**: Expanded protocol module implementations
- **Improved Documentation**: Detailed implementation guides for each protocol module
- **Performance Optimization**: Module-specific performance enhancements
- **Extended Integration**: Additional inter-module integration patterns

## References

### Normative

- [Logos Core Architecture RFC](./logos-core-architecture.md)
- [Logos Authentication and Capability System RFC](./logos-authentication-capability-system.md)
- [Logos Core Proof of Concept - Specifications](https://github.com/logos-co/logos-core-poc/blob/develop/docs/specs.md)

### Informative

- [Waku Protocol Documentation](https://waku.org)
- [IRC Protocol RFC 1459](https://tools.ietf.org/html/rfc1459)

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
