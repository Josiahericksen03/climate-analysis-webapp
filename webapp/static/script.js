// Climate Analysis Website JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Navbar background change on scroll
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('bg-dark');
            navbar.style.backgroundColor = 'rgba(44, 62, 80, 0.95)';
        } else {
            navbar.classList.remove('bg-dark');
            navbar.style.backgroundColor = 'transparent';
        }
    });

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe all cards and sections
    document.querySelectorAll('.card, .analysis-card').forEach(el => {
        observer.observe(el);
    });

    // Analysis form handling
    const analysisForm = document.getElementById('analysisForm');
    const stationSelect = document.getElementById('stationSelect');
    const analysisTypeSelect = document.getElementById('analysisType');
    
    // Handle clustering selection - auto-select "All Stations"
    if (analysisTypeSelect) {
        analysisTypeSelect.addEventListener('change', function() {
            if (this.value === 'clustering') {
                stationSelect.value = 'all';
                stationSelect.disabled = true;
                stationSelect.classList.add('bg-light');
                // Add a small note
                const note = document.createElement('small');
                note.className = 'text-muted d-block mt-1';
                note.textContent = 'All stations are required for clustering analysis';
                stationSelect.parentNode.appendChild(note);
            } else {
                stationSelect.disabled = false;
                stationSelect.classList.remove('bg-light');
                // Remove the note if it exists
                const note = stationSelect.parentNode.querySelector('small');
                if (note) note.remove();
            }
        });
    }
    
    if (analysisForm) {
        analysisForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading"></span> Analyzing...';
            submitBtn.disabled = true;

            // Get form data
            const formData = new FormData(this);
            
            // Make API call to backend
            fetch('/analyze', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Reset button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                
                if (data.success) {
                    // Show results
                    showAnalysisResults(data);
                    
                    // Show cache status
                    if (data.cached) {
                        showNotification('Results loaded from cache (fast!)', 'success');
                    } else {
                        showNotification('Analysis completed! (First time generation)', 'success');
                    }
                } else {
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                // Reset button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                
                showNotification('Analysis failed. Please try again.', 'error');
                console.error('Error:', error);
            });
        });
    }

    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });

        // Close mobile menu when clicking on a link
        const mobileNavLinks = navbarCollapse.querySelectorAll('.nav-link');
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', function() {
                navbarCollapse.classList.remove('show');
            });
        });
    }
});

// Helper Functions

function showAnalysisResults(data) {
    // Create and show results modal or section
    const resultsSection = document.getElementById('analysisResults');
    const plotsContainer = document.getElementById('plotsContainer');
    const analysisSummary = document.getElementById('analysisSummary');
    
    if (resultsSection && plotsContainer) {
        // Clear previous plots
        plotsContainer.innerHTML = '';
        
        // Show analysis summary if available
        if (data.data_summary) {
            analysisSummary.innerHTML = `
                <strong>Analysis Summary:</strong> 
                ${data.data_summary.total_records} records analyzed from ${data.data_summary.stations} stations 
                (${data.data_summary.date_range})
            `;
            analysisSummary.style.display = 'block';
        }
        
        // Display plots if available
        if (data.plots && data.plots.length > 0) {
            data.plots.forEach((plot, index) => {
                const plotDiv = document.createElement('div');
                plotDiv.className = 'col-12 mb-4';
                
                // Determine plot title based on filename
                let plotTitle = 'Analysis Plot';
                if (plot.includes('trend_analysis')) {
                    plotTitle = 'Temperature Trends & Predictions';
                } else if (plot.includes('anomaly_analysis')) {
                    plotTitle = 'Anomaly Detection';
                } else if (plot.includes('prediction_')) {
                    plotTitle = 'Future Predictions';
                } else if (plot.includes('climate_clusters')) {
                    plotTitle = 'Regional Climate Clusters';
                }
                
                plotDiv.innerHTML = `
                    <div class="plot-container">
                        <h5 class="mb-3">${plotTitle}</h5>
                        <img src="/static/${plot}?t=${Date.now()}" 
                             alt="${plotTitle}" class="img-fluid rounded shadow">
                        <p class="text-center mt-2"><small>${plot.replace('.png', '').replace(/_/g, ' ')}</small></p>
                    </div>
                `;
                
                plotsContainer.appendChild(plotDiv);
            });
        } else {
            // Show message if no plots generated
            plotsContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        No plots were generated for this analysis. Please try a different selection.
                    </div>
                </div>
            `;
        }
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
        // Show success notification
        showNotification('Analysis completed successfully!', 'success');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 100px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Export functions for analysis
function exportAnalysis() {
    // Implementation for exporting analysis results
    showNotification('Analysis exported successfully!', 'success');
}

function shareResults() {
    // Implementation for sharing results
    if (navigator.share) {
        navigator.share({
            title: 'Climate Analysis Results',
            text: 'Check out my climate change impact analysis!',
            url: window.location.href
        });
    } else {
        // Fallback for browsers that don't support Web Share API
        navigator.clipboard.writeText(window.location.href);
        showNotification('Link copied to clipboard!', 'info');
    }
}

// Performance optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Optimize scroll events
const optimizedScrollHandler = debounce(function() {
    // Scroll-based animations and effects
}, 16);

window.addEventListener('scroll', optimizedScrollHandler); 