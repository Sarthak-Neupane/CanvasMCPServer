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

Add to your Claude Desktop configuration: (You might need to add full path to the directory)

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

### Available Tools
Canvas Course Management

#### get_all_courses: 
Retrieve all accessible courses with pagination support
Filter by enrollment state, type, and workflow state
Include additional fields: syllabus, teachers, sections, student counts, etc.
Smart pagination (return all or limit results)

#### get_course_by_id: 
Get detailed information about a specific course
Access course metadata, permissions, and detailed content
Include teachers, sections, progress tracking, and more

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
