---
title: LOGOS-MODULE-DEVELOPMENT-GUIDE
name: Logos Module Development Guide
status: raw
category: Standards Track
tags: logos-core, module-development, qt-plugins, process-isolation
editor: Logos Core Team
contributors:
- Filip Dimitrijevic <filip@status.im>
---

## Abstract

This RFC documents the module development requirements for the Logos Core Platform as specified in the current implementation. It covers the verified module interface requirements, the optional initLogos method, and development considerations based on the platform's modular architecture.

## Background / Rationale / Motivation

The Logos Core Platform uses a modular architecture where independently developed modules run in separate processes. This guide documents the module development requirements as specified in the current implementation.

## Module Creation Walkthrough

### Step 1: Interface Definition

All modules must implement a common interface as specified in the platform requirements. The exact interface definition is not fully detailed in the current specifications, but modules are required to integrate with the platform's Qt-based architecture.

### Step 2: Module Implementation

As specified in the documentation, modules can optionally implement the `initLogos(LogosAPI*)` method:

> "when a module calls `registerObject(name, object)`, the provider optionally calls `object->initLogos(LogosAPI*)`"

```cpp
class MyModule : public QObject {
    Q_OBJECT

public:
    // Optional initialization method as documented
    virtual void initLogos(LogosAPI* api);

    // Module methods for inter-module communication
    // (specific requirements not detailed in current specs)
};
```

### Step 3: Metadata Configuration

Module metadata requirements are referenced in the specifications but the exact format is not detailed in the current documentation. Modules require metadata for proper integration with the platform.

### Step 4: Build System Setup

Build system configuration details are not specified in the current documentation. Modules are expected to be Qt plugins that integrate with the platform's modular architecture.

## Module Integration Requirements

### LogosAPI Integration

As specified in the documentation, modules integrate with the platform through the LogosAPI:

- Modules can optionally implement `initLogos(LogosAPI*)` method
- This method is called when a module registers an object with the platform
- The LogosAPI provides access to inter-module communication capabilities

### Platform Architecture Requirements

Based on the specifications:

- Modules are Qt-based plugins (as referenced in the specifications)
- Each module runs in a separate process for isolation (as documented)
- Inter-module communication uses a Remote Procedure Call (RPC) mechanism
- The platform supports methods with up to 5 arguments (as specified)
- Return types include: void, bool, int, QString, QVariant (as documented)

## Module Development Process

### Implementation Requirements

Based on the specifications:

1. **Module Interface**: Implement the common interface (specific requirements not detailed in current specs)
2. **Optional Initialization**: Optionally implement `initLogos(LogosAPI*)` as documented
3. **Qt Plugin Structure**: Structure the module as a Qt plugin (as referenced in specifications)
4. **Metadata Configuration**: Provide metadata (format not detailed in current specs)

### Platform Integration

Modules integrate with the platform through:

- **LogosAPI**: Access to inter-module communication
- **Process Isolation**: Each module runs in its own process
- **Authentication**: Token-based authentication for inter-module calls
- **RPC Communication**: Remote Procedure Call mechanism for communication

### LogosAPI Usage

As documented, the `initLogos(LogosAPI*)` method provides access to:

- Inter-module communication capabilities
- Platform integration features
- Authentication and capability management

The specific API details and usage patterns are part of the C++ SDK implementation.

## Security/Privacy Considerations

### Module Isolation

- **Process Boundaries**: Each module runs in a separate process as enforced by the platform
- **Authentication Requirements**: All inter-module calls require valid authentication tokens
- **Capability Restrictions**: Modules must request access to other modules through the Capability Module

### Development Security

- **Process Isolation**: Modules benefit from operating system-level process boundaries
- **Authentication Integration**: Modules must integrate with the platform's token-based authentication system

## Implementation Suggestions

### Development Considerations

- **Process Isolation**: Design modules to work within the process-isolated architecture
- **Communication Limitations**: Respect the platform's method call limitations (up to 5 arguments)
- **Return Types**: Use supported return types (void, bool, int, QString, QVariant, QJsonArray, QStringList)
- **Qt Plugin Requirements**: Follow Qt plugin structure as referenced in the specifications

## Future Enhancements

As noted in the specifications, this is a "living document" that may not fully reflect the ultimate design. The current implementation represents a proof-of-concept stage.

## References

### Normative

- [Logos Core Architecture RFC](./logos-core-architecture.md)
- [Logos Authentication and Capability System RFC](./logos-authentication-capability-system.md)
- [Logos Core Proof of Concept - Specifications](https://github.com/logos-co/logos-core-poc/blob/develop/docs/specs.md)

### Informative

- [Qt Plugin Development](https://doc.qt.io/qt-6/plugins-howto.html)
- [Qt Remote Objects Documentation](https://doc.qt.io/qt-6/qtremoteobjects-index.html)

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
