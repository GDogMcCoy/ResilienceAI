/**
 * ResilienceAI Graph Visualization Component
 * Interactive D3.js-based graph visualization
 */

class ResilienceGraphVisualization {
    constructor(containerId, options = {}) {
        this.container = d3.select(`#${containerId}`);
        this.width = options.width || 800;
        this.height = options.height || 600;
        this.nodeRadius = options.nodeRadius || 8;
        this.linkDistance = options.linkDistance || 100;
        
        // Color scales
        this.riskColorScale = d3.scaleSequential(d3.interpolateReds)
            .domain([0, 1]);
        this.resilienceColorScale = d3.scaleSequential(d3.interpolateGreens)
            .domain([0, 1]);
        
        this.init();
    }
    
    init() {
        // Create SVG container
        this.svg = this.container.append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('viewBox', [0, 0, this.width, this.height]);
        
        // Add zoom behavior
        this.zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });
        
        this.svg.call(this.zoom);
        
        // Create main group
        this.g = this.svg.append('g');
        
        // Define arrow markers
        this.svg.append('defs').selectAll('marker')
            .data(['end'])
            .enter().append('marker')
            .attr('id', 'arrow')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 25)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#999');
        
        // Initialize tooltip
        this.tooltip = d3.select('body').append('div')
            .attr('class', 'graph-tooltip')
            .style('opacity', 0)
            .style('position', 'absolute')
            .style('background', 'rgba(0, 0, 0, 0.8)')
            .style('color', 'white')
            .style('padding', '10px')
            .style('border-radius', '5px')
            .style('pointer-events', 'none')
            .style('font-size', '12px');
    }
    
    render(data, options = {}) {
        const { nodes, links } = data;
        const colorBy = options.colorBy || 'risk_score';
        const sizeBy = options.sizeBy || 'population';
        
        // Create simulation
        this.simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(this.linkDistance))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(d => this.getNodeSize(d, sizeBy) + 5));
        
        // Render links
        this.linkElements = this.g.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(links)
            .enter().append('line')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => Math.sqrt(d.weight || 1))
            .attr('marker-end', d => d.directed ? 'url(#arrow)' : null);
        
        // Render nodes
        this.nodeElements = this.g.append('g')
            .attr('class', 'nodes')
            .selectAll('circle')
            .data(nodes)
            .enter().append('circle')
            .attr('r', d => this.getNodeSize(d, sizeBy))
            .attr('fill', d => this.getNodeColor(d, colorBy))
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)
            .call(d3.drag()
                .on('start', (event, d) => this.dragstarted(event, d))
                .on('drag', (event, d) => this.dragged(event, d))
                .on('end', (event, d) => this.dragended(event, d)));
        
        // Add labels
        this.labelElements = this.g.append('g')
            .attr('class', 'labels')
            .selectAll('text')
            .data(nodes)
            .enter().append('text')
            .text(d => d.name)
            .attr('font-size', '10px')
            .attr('dx', 12)
            .attr('dy', '.35em')
            .style('pointer-events', 'none');
        
        // Add interactivity
        this.nodeElements
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mouseout', () => this.hideTooltip())
            .on('click', (event, d) => this.handleNodeClick(d));
        
        // Update positions on tick
        this.simulation.on('tick', () => this.ticked());
    }
    
    getNodeColor(node, colorBy) {
        if (colorBy === 'risk_score') {
            return this.riskColorScale(node.risk_score || 0);
        } else if (colorBy === 'resilience_score') {
            return this.resilienceColorScale(node.resilience_score || 0);
        } else if (colorBy === 'type') {
            const typeColors = {
                'County': '#1f77b4',
                'Facility': '#ff7f0e',
                'Infrastructure': '#2ca02c',
                'Hazard': '#d62728',
                'Organization': '#9467bd'
            };
            return typeColors[node.type] || '#999';
        }
        return '#1f77b4';
    }
    
    getNodeSize(node, sizeBy) {
        if (sizeBy === 'population') {
            return Math.sqrt((node.population || 0) / 10000) + 5;
        } else if (sizeBy === 'criticality') {
            return (node.criticality || 1) * 3;
        }
        return this.nodeRadius;
    }
    
    ticked() {
        this.linkElements
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        this.nodeElements
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        this.labelElements
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    }
    
    showTooltip(event, d) {
        const content = `
            <strong>${d.name}</strong><br/>
            Type: ${d.type || 'Unknown'}<br/>
            Risk Score: ${(d.risk_score || 0).toFixed(2)}<br/>
            Resilience: ${(d.resilience_score || 0).toFixed(2)}<br/>
            ${d.population ? `Population: ${d.population.toLocaleString()}<br/>` : ''}
            ${d.state ? `State: ${d.state}<br/>` : ''}
        `;
        
        this.tooltip
            .html(content)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .transition()
            .duration(200)
            .style('opacity', 1);
    }
    
    hideTooltip() {
        this.tooltip.transition()
            .duration(200)
            .style('opacity', 0);
    }
    
    handleNodeClick(node) {
        // Emit event for external handling
        const event = new CustomEvent('graphNodeClick', { detail: node });
        document.dispatchEvent(event);
        
        // Highlight connected nodes
        this.highlightNeighbors(node);
    }
    
    highlightNeighbors(centerNode) {
        const connectedNodeIds = new Set();
        connectedNodeIds.add(centerNode.id);
        
        this.linkElements.each(d => {
            if (d.source.id === centerNode.id) {
                connectedNodeIds.add(d.target.id);
            } else if (d.target.id === centerNode.id) {
                connectedNodeIds.add(d.source.id);
            }
        });
        
        this.nodeElements
            .transition()
            .duration(300)
            .style('opacity', d => connectedNodeIds.has(d.id) ? 1 : 0.2);
        
        this.linkElements
            .transition()
            .duration(300)
            .style('opacity', d => 
                d.source.id === centerNode.id || d.target.id === centerNode.id ? 1 : 0.1
            );
    }
    
    resetHighlight() {
        this.nodeElements.transition().duration(300).style('opacity', 1);
        this.linkElements.transition().duration(300).style('opacity', 0.6);
    }
    
    dragstarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    dragended(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    zoomToNode(nodeId, scale = 2) {
        const node = this.nodeElements.data().find(d => d.id === nodeId);
        if (!node) return;
        
        this.svg.transition()
            .duration(750)
            .call(
                this.zoom.transform,
                d3.zoomIdentity
                    .translate(this.width / 2, this.height / 2)
                    .scale(scale)
                    .translate(-node.x, -node.y)
            );
    }
    
    exportSVG() {
        const svgData = new XMLSerializer().serializeToString(this.svg.node());
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'graph-visualization.svg';
        link.click();
        
        URL.revokeObjectURL(url);
    }
    
    destroy() {
        // Clean up
        this.simulation.stop();
        this.svg.remove();
        this.tooltip.remove();
    }
}


// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResilienceGraphVisualization;
}
