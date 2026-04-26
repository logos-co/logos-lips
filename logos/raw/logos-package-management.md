---
title: LOGOS-PACKAGE-MANAGEMENT
name: Logos Package Management and Distribution
status: raw
category: Standards Track
tags: logos-core, package-management, module-distribution, plugin-loading
editor: Logos Core Team
contributors:
- Filip Dimitrijevic <filip@status.im>
---

## Abstract

This RFC documents the package management and distribution capabilities of the Logos Core Platform as specified in the current implementation. It covers the verified module management functions including module discovery, loading, unloading, and metadata processing that are documented in the platform specifications.

## Background / Rationale / Motivation

The Logos Core Platform operates as a modular, plugin-based runtime system where modules can be dynamically managed. The platform provides core functionality for:

- **Module Discovery**: Identifying available modules in the system
- **Dynamic Loading**: Loading modules at runtime
- **Module Management**: Unloading and managing module lifecycle
- **Metadata Processing**: Reading and processing module metadata

This RFC documents the package management capabilities as they exist in the current proof-of-concept implementation.

## Module Management System

### Core Module Management Functions

Based on the specifications, the platform provides these documented functions:

#### Module Discovery and Processing

- `logos_core_get_known_plugins()` - Returns a list of all modules discovered, even if not loaded
- `logos_core_process_plugin(const char* path)` - Reads a module file's metadata and adds it to the list of known modules without loading it

#### Module Lifecycle Management

- `logos_core_get_loaded_plugins()` - Returns a list of currently loaded modules (names)
- `logos_core_load_plugin(const char* name)` - Loads a module by name, starts a logos_host process, sends an auth token, waits for the module to register and records it as loaded
- `logos_core_unload_plugin(const char* name)` - Terminates the module's process and removes it from loaded modules

### Package Manager Module Reference

The specifications reference a "Package Manager" module in the system architecture, but detailed implementation specifics are not provided in the current documentation.

## Module Distribution Architecture

### Plugin-Based System

As documented in the specifications, the platform operates as a:

- **Plugin-based runtime**: Modules are implemented as Qt Plugins
- **Modular system**: Supports independently developed modules
- **Process-isolated architecture**: Each module runs in a separate process

### Module Format

As referenced in the specifications:

- **Plugin-Based**: Platform described as "plugin-based runtime"
- **Metadata Support**: Modules include metadata (referenced in `logos_core_process_plugin()` function)
- **Process Integration**: Modules work with logos_host process system (mentioned in loading process)

## Module Installation Process

### Loading Mechanism

Based on the `logos_core_load_plugin()` function documentation:

"Loads a module by name. Starts a logos_host process, sends an auth token, waits for the module to register and records it as loaded."

### Module Management

As documented in the specifications:

- **Known Module Tracking**: `logos_core_get_known_plugins()` returns discovered modules
- **Loaded Module Tracking**: `logos_core_get_loaded_plugins()` returns currently loaded modules
- **Module Processing**: `logos_core_process_plugin()` reads metadata without loading
- **Module Loading/Unloading**: Platform provides load and unload functions

## Module Metadata System

### Metadata Processing

As specified in the documentation:

- **Metadata Reading**: `logos_core_process_plugin()` "reads a module file's metadata and adds it to the list of known modules without loading it"

### Module Information

Based on the documented functions:

- **Module Names**: Functions work with module names (as parameters)
- **Module Status**: Platform distinguishes between known and loaded modules (via separate functions)
- **Module Paths**: `logos_core_process_plugin()` takes file paths as input

## Security/Privacy Considerations

### Module Authentication

- **Token-Based Security**: Each loaded module receives an authentication token
- **Process Isolation**: Modules run in separate processes for security
- **Controlled Loading**: Platform mediates all module loading operations

### Module Management Security

- **Process Isolation**: Each module runs in a separate process as documented
- **Authentication Integration**: Module loading includes authentication token handling as specified

## Implementation Considerations

### Current Implementation Status

Based on the specifications:

- **Core Functions Available**: Module management functions are documented in the API
- **Process Integration**: logos_host process system is referenced in module loading
- **Authentication Support**: Token-based authentication is mentioned in module loading process
- **Qt Plugin Support**: Platform is described as plugin-based runtime

### Module Development

Based on the specifications:

- **Qt Plugin Format**: Platform operates as plugin-based runtime (as documented)
- **Metadata Requirements**: Modules include metadata that can be processed (as referenced in process_plugin function)
- **Authentication Integration**: Modules receive authentication tokens during loading (as specified)
- **Process Architecture**: Modules run in separate processes (as documented)

## Future Enhancements

As noted in the specifications, this is a "living document" that may not fully reflect the ultimate design. Areas for potential development include:

- **Enhanced Package Management**: More sophisticated package management capabilities
- **Dependency Resolution**: Automated dependency management systems
- **Version Management**: Comprehensive versioning and compatibility systems
- **Distribution Mechanisms**: Advanced module distribution and installation systems

## References

### Normative

- [Logos Core Architecture RFC](./logos-core-architecture.md)
- [Logos Module Development Guide RFC](./logos-module-development-guide.md)
- [Logos Core Proof of Concept - Specifications](https://github.com/logos-co/logos-core-poc/blob/develop/docs/specs.md)

### Informative

- [Qt Plugin Development](https://doc.qt.io/qt-6/plugins-howto.html)

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
