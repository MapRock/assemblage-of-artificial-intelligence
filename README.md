# The Assemblage of Artificial Intelligence

A blog exploring artificial intelligence through the lens of assemblage theory, examining how AI systems emerge from complex interactions between technical components, data flows, social structures, and human agency.

## Overview

This project implements a static blog website that explores AI not as isolated technological systems, but as complex assemblages of heterogeneous components including:

- Technical infrastructure (algorithms, hardware, software)
- Data flows and information networks
- Human labor and social practices
- Institutional frameworks and power relations
- Material resources and environmental impacts

## Features

- **Responsive Design**: Mobile-friendly interface with modern CSS
- **Dynamic Content Loading**: JavaScript-powered blog post management
- **Academic Focus**: In-depth articles on AI theory and critical perspectives
- **Extensible Architecture**: Easy to add new posts and features

## Structure

```
├── index.html              # Main blog homepage
├── styles/
│   └── main.css            # Primary stylesheet
├── scripts/
│   └── blog.js             # Blog functionality and post management
├── content/
│   └── posts.json          # Blog post metadata and configuration
├── posts/
│   ├── understanding-ai-as-assemblage.md
│   └── materiality-of-machine-learning.md
└── README.md
```

## Running the Blog

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/MapRock/assemblage-of-artificial-intelligence.git
   cd assemblage-of-artificial-intelligence
   ```

2. Start a local web server:
   ```bash
   python3 -m http.server 8000
   # or
   npm start
   ```

3. Open your browser to `http://localhost:8000`

### Adding New Posts

1. Create a new Markdown file in the `posts/` directory
2. Add post metadata to `content/posts.json`
3. The blog will automatically load and display the new content

## Content Themes

The blog explores several key themes:

- **Assemblage Theory**: Understanding AI as heterogeneous networks rather than unified systems
- **Materiality**: The physical infrastructure and resources underlying AI systems  
- **Human-AI Relations**: How human labor and social structures intertwine with AI
- **Power and Governance**: How AI systems participate in and reshape power relations
- **Environmental Impact**: The ecological consequences of AI development and deployment

## Technical Implementation

- **Pure HTML/CSS/JavaScript**: No framework dependencies for maximum compatibility
- **Progressive Enhancement**: Works without JavaScript, enhanced with it
- **Semantic HTML**: Accessible and SEO-friendly markup
- **Modular CSS**: Organized stylesheets using CSS custom properties
- **Modern JavaScript**: ES6+ features with graceful degradation

## Contributing

This project welcomes contributions including:

- New blog posts on related themes
- Improvements to the technical implementation
- Bug fixes and accessibility enhancements
- Translations and internationalization

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Academic Context

This blog engages with scholarship from:
- Science and Technology Studies (STS)
- Critical Data Studies
- Digital Sociology
- Philosophy of Technology
- Media Archaeology
- Postcolonial Science and Technology Studies