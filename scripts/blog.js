/**
 * Blog functionality for The Assemblage of Artificial Intelligence
 */

class BlogManager {
    constructor() {
        this.posts = [];
        this.postsContainer = document.getElementById('posts-container');
        this.init();
    }

    init() {
        this.loadPosts();
        this.setupNavigation();
    }

    async loadPosts() {
        try {
            // Show loading state
            this.showLoading();
            
            // Load posts from JSON file or API
            const response = await fetch('./content/posts.json');
            if (response.ok) {
                this.posts = await response.json();
            } else {
                // Fallback to default posts if file doesn't exist
                this.posts = this.getDefaultPosts();
            }
            
            this.renderPosts();
        } catch (error) {
            console.log('Loading default posts due to error:', error.message);
            this.posts = this.getDefaultPosts();
            this.renderPosts();
        }
    }

    getDefaultPosts() {
        return [
            {
                id: 1,
                title: "Understanding AI as Assemblage",
                excerpt: "Exploring how artificial intelligence emerges from complex interactions between algorithms, data, infrastructure, and human practices rather than existing as isolated systems.",
                date: "2025-01-14",
                slug: "understanding-ai-as-assemblage",
                content: "posts/understanding-ai-as-assemblage.md"
            },
            {
                id: 2,
                title: "The Materiality of Machine Learning",
                excerpt: "Examining the physical infrastructure, energy consumption, and material resources that underpin seemingly ethereal AI systems.",
                date: "2025-01-10",
                slug: "materiality-of-machine-learning",
                content: "posts/materiality-of-machine-learning.md"
            },
            {
                id: 3,
                title: "Human-AI Entanglements",
                excerpt: "How human labor, cognitive processes, and social structures become intertwined with AI systems in unexpected ways.",
                date: "2025-01-05",
                slug: "human-ai-entanglements",
                content: "posts/human-ai-entanglements.md"
            },
            {
                id: 4,
                title: "Data Flows and Power Networks",
                excerpt: "Analyzing how data circulation creates new forms of power relations and governance in AI-driven societies.",
                date: "2025-01-01",
                slug: "data-flows-and-power-networks",
                content: "posts/data-flows-and-power-networks.md"
            }
        ];
    }

    showLoading() {
        if (this.postsContainer) {
            this.postsContainer.innerHTML = '<div class="loading">Loading posts...</div>';
        }
    }

    renderPosts() {
        if (!this.postsContainer) return;

        const postsHTML = this.posts.map(post => `
            <article class="post-card" data-post-id="${post.id}">
                <h3 class="post-title">${post.title}</h3>
                <p class="post-excerpt">${post.excerpt}</p>
                <div class="post-meta">
                    <span class="post-date">${this.formatDate(post.date)}</span>
                    <a href="#" class="read-more" data-slug="${post.slug}">Read More →</a>
                </div>
            </article>
        `).join('');

        this.postsContainer.innerHTML = postsHTML;

        // Add click handlers for read more links
        this.postsContainer.querySelectorAll('.read-more').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const slug = e.target.getAttribute('data-slug');
                this.openPost(slug);
            });
        });
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    openPost(slug) {
        const post = this.posts.find(p => p.slug === slug);
        if (post) {
            // In a real implementation, this would navigate to a post page
            // For now, we'll show an alert
            alert(`Opening post: ${post.title}\n\nThis would typically load the full post content from ${post.content}`);
        }
    }

    setupNavigation() {
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Method to add new posts (for future expansion)
    addPost(post) {
        this.posts.unshift(post);
        this.renderPosts();
    }

    // Method to search posts (for future expansion)
    searchPosts(query) {
        return this.posts.filter(post => 
            post.title.toLowerCase().includes(query.toLowerCase()) ||
            post.excerpt.toLowerCase().includes(query.toLowerCase())
        );
    }
}

// Initialize blog when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BlogManager();
});

// Export for potential use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BlogManager;
}