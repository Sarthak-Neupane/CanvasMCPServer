# Canvas MCP Server

A Model Context Protocol (MCP) server that provides Canvas-related tools for AI assistants.

## Features

- 🎨 Canvas tool integration
- 🔧 Extensible tool architecture
- 🚀 Fast and lightweight

## Installation

### From Source

```bash
git clone https://github.com/sarthakneupane/canvas-mcp-server.git
cd canvas-mcp-server
pip install -e .
```

### Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API credentials:
   ```bash
   CANVAS_API_TOKEN=your_actual_api_token_here
   CANVAS_BASE_URL=https://your-api.example.com
   ```

### Development Installation

```bash
git clone https://github.com/sarthakneupane/canvas-mcp-server.git
cd canvas-mcp-server
pip install -e ".[dev]"
```

## Usage

### As a Standalone Server

```bash
canvas-mcp-server
```

### With Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "canvas-mcp-server": {
      "command": "canvas-mcp-server"
    }
  }
}
```

### Programmatic Usage

```python
from canvas_mcp_server import main

# Run the server
main()
```

## Available Tools

- **hello_world**: A simple greeting tool for testing
- **api_request**: Make API requests using configured credentials

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/ --strict
```

## Project Structure

```
canvas-mcp-server/
├── src/canvas_mcp_server/    # Main package
│   ├── server.py             # Server implementation
│   └── tools/                # Available tools
├── tests/                    # Test suite
├── examples/                 # Usage examples
└── scripts/                  # Development scripts
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Sarthak Neupane**

- GitHub: [@Sarthak-Neupane](https://github.com/Sarthak-Neupane)
