/**
 * Astrological Chart Wheel Visualization
 * Creates a circular natal chart with houses and planets
 */

// Zodiac sign symbols
const ZODIAC_SYMBOLS = {
    'Aries': '♈',
    'Taurus': '♉',
    'Gemini': '♊',
    'Cancer': '♋',
    'Leo': '♌',
    'Virgo': '♍',
    'Libra': '♎',
    'Scorpio': '♏',
    'Sagittarius': '♐',
    'Capricorn': '♑',
    'Aquarius': '♒',
    'Pisces': '♓'
};

// Planet symbols
const PLANET_SYMBOLS = {
    'Sun': '☉',
    'Moon': '☽',
    'Mercury': '☿',
    'Venus': '♀',
    'Mars': '♂',
    'Jupiter': '♃',
    'Saturn': '♄',
    'Uranus': '♅',
    'Neptune': '♆',
    'Pluto': '♇',
    'Chiron': '⚷'
};

// Sign to degree mapping (0-360, Aries starts at 0)
const SIGN_DEGREES = {
    'Aries': 0,
    'Taurus': 30,
    'Gemini': 60,
    'Cancer': 90,
    'Leo': 120,
    'Virgo': 150,
    'Libra': 180,
    'Scorpio': 210,
    'Sagittarius': 240,
    'Capricorn': 270,
    'Aquarius': 300,
    'Pisces': 330
};

class ChartWheel {
    constructor(canvasId, chartData) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Canvas element not found:', canvasId);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.chartData = chartData;
        
        // Set canvas size with device pixel ratio for crisp rendering
        this.dpr = window.devicePixelRatio || 1;
        this.size = 600;
        this.canvas.width = this.size * this.dpr;
        this.canvas.height = this.size * this.dpr;
        
        this.ctx.scale(this.dpr, this.dpr);
        
        this.centerX = this.size / 2;
        this.centerY = this.size / 2;
        
        // Radii for different chart elements
        this.outerRadius = 280;
        this.zodiacInnerRadius = 240;
        this.innerRadius = 200;
        this.planetRadius = 170;
        this.aspectRadius = 150;
        this.centerRadius = 60;
        
        // Aspect orbs (tolerance in degrees)
        this.aspects = {
            conjunction: { angle: 0, orb: 8, color: '#FF6B6B', name: 'Conjunction' },
            opposition: { angle: 180, orb: 8, color: '#E74C3C', name: 'Opposition' },
            trine: { angle: 120, orb: 8, color: '#3498DB', name: 'Trine' },
            square: { angle: 90, orb: 8, color: '#E67E22', name: 'Square' },
            sextile: { angle: 60, orb: 6, color: '#9B59B6', name: 'Sextile' }
        };
        
        this.draw();
    }
    
    draw() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.size, this.size);
        
        // Draw components in order (back to front)
        this.drawBackground();
        this.drawInnerCircle();
        this.drawAspectLines();
        this.drawZodiacWheel();
        this.drawHouseLines();
        this.drawHouseNumbers();
        this.drawPlanets();
        this.drawCenterInfo();
    }
    
    drawBackground() {
        // Outer background circle
        this.ctx.fillStyle = '#2c3e50';
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, this.outerRadius, 0, Math.PI * 2);
        this.ctx.fill();
    }
    
    drawInnerCircle() {
        // White inner circle for chart content
        this.ctx.fillStyle = '#ffffff';
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, this.zodiacInnerRadius, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Subtle inner rings for depth
        this.ctx.strokeStyle = '#e0e0e0';
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, this.innerRadius, 0, Math.PI * 2);
        this.ctx.stroke();
        
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, this.aspectRadius, 0, Math.PI * 2);
        this.ctx.stroke();
    }
    
    drawZodiacWheel() {
        const zodiacOrder = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ];
        
        const degreesPerSign = 30;
        
        // Get Ascendant position for rotation
        const ascendant = this.chartData.houses[1];
        const ascendantAbsoluteDegree = SIGN_DEGREES[ascendant.sign] + ascendant.degree;
        
        zodiacOrder.forEach((sign, index) => {
            // Calculate angles for zodiac ring relative to Ascendant
            const astroStart = index * degreesPerSign;
            const astroEnd = (index + 1) * degreesPerSign;
            const startAngle = (180 - (astroStart - ascendantAbsoluteDegree)) * Math.PI / 180;
            const endAngle = (180 - (astroEnd - ascendantAbsoluteDegree)) * Math.PI / 180;
            
            // Draw zodiac segments (going counterclockwise, so swap start/end)
            this.ctx.fillStyle = '#2c3e50';
            this.ctx.beginPath();
            this.ctx.arc(this.centerX, this.centerY, this.outerRadius, endAngle, startAngle);
            this.ctx.arc(this.centerX, this.centerY, this.zodiacInnerRadius, startAngle, endAngle, true);
            this.ctx.closePath();
            this.ctx.fill();
            
            // Draw separator lines
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            const lineX = this.centerX + Math.cos(startAngle) * this.zodiacInnerRadius;
            const lineY = this.centerY + Math.sin(startAngle) * this.zodiacInnerRadius;
            this.ctx.moveTo(lineX, lineY);
            const lineX2 = this.centerX + Math.cos(startAngle) * this.outerRadius;
            const lineY2 = this.centerY + Math.sin(startAngle) * this.outerRadius;
            this.ctx.lineTo(lineX2, lineY2);
            this.ctx.stroke();
            
            // Draw zodiac symbol and name
            const midAngle = (startAngle + endAngle) / 2;
            const symbolRadius = (this.outerRadius + this.zodiacInnerRadius) / 2;
            const x = this.centerX + Math.cos(midAngle) * symbolRadius;
            const y = this.centerY + Math.sin(midAngle) * symbolRadius;
            
            // Symbol
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = 'bold 20px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(ZODIAC_SYMBOLS[sign], x, y - 8);
            
            // Name
            this.ctx.font = '10px Arial';
            this.ctx.fillText(sign.toUpperCase(), x, y + 10);
        });
        
        // Draw outer and inner borders
        this.ctx.strokeStyle = '#ffffff';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, this.outerRadius, 0, Math.PI * 2);
        this.ctx.stroke();
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, this.zodiacInnerRadius, 0, Math.PI * 2);
        this.ctx.stroke();
    }
    
    calculateAngle(sign, degree) {
        // Convert sign + degree to absolute degree (0-360)
        // Aries = 0°, Taurus = 30°, etc.
        const signBase = SIGN_DEGREES[sign];
        const absoluteDegree = signBase + degree;
        
        // Get the Ascendant (1st house cusp) position
        const ascendant = this.chartData.houses[1];
        const ascendantAbsoluteDegree = SIGN_DEGREES[ascendant.sign] + ascendant.degree;
        
        // Calculate angle relative to Ascendant
        // Rotate so Ascendant is at 180° (left side, 9 o'clock)
        const relativeToAscendant = absoluteDegree - ascendantAbsoluteDegree;
        const canvasAngle = (180 - relativeToAscendant) * Math.PI / 180;
        
        return canvasAngle;
    }
    
    drawHouseLines() {
        this.ctx.strokeStyle = '#2c3e50';
        this.ctx.lineWidth = 1.5;
        
        // Draw lines from center to zodiac ring for each house cusp
        for (let houseNum = 1; houseNum <= 12; houseNum++) {
            const house = this.chartData.houses[houseNum];
            if (!house) continue;
            
            const angle = this.calculateAngle(house.sign, house.degree);
            
            const x1 = this.centerX + Math.cos(angle) * this.centerRadius;
            const y1 = this.centerY + Math.sin(angle) * this.centerRadius;
            const x2 = this.centerX + Math.cos(angle) * this.zodiacInnerRadius;
            const y2 = this.centerY + Math.sin(angle) * this.zodiacInnerRadius;
            
            // Use dashed line for houses 2-12, solid for house 1 (Ascendant)
            if (houseNum === 1 || houseNum === 10) {
                this.ctx.setLineDash([]);
                this.ctx.lineWidth = 2;
            } else {
                this.ctx.setLineDash([5, 5]);
                this.ctx.lineWidth = 1;
            }
            
            this.ctx.beginPath();
            this.ctx.moveTo(x1, y1);
            this.ctx.lineTo(x2, y2);
            this.ctx.stroke();
        }
        
        this.ctx.setLineDash([]);
    }
    
    drawHouseNumbers() {
        this.ctx.font = 'bold 14px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        for (let houseNum = 1; houseNum <= 12; houseNum++) {
            const house = this.chartData.houses[houseNum];
            const nextHouse = this.chartData.houses[houseNum === 12 ? 1 : houseNum + 1];
            
            if (!house || !nextHouse) continue;
            
            // Calculate midpoint between this house and next house cusp
            const angle1 = this.calculateAngle(house.sign, house.degree);
            const angle2 = this.calculateAngle(nextHouse.sign, nextHouse.degree);
            
            // Handle angle wraparound properly
            let midAngle;
            let angleDiff = angle1 - angle2;
            
            // Normalize angle difference to -PI to PI range
            while (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
            while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;
            
            // Calculate midpoint
            midAngle = angle2 + angleDiff / 2;
            
            const radius = (this.zodiacInnerRadius + this.innerRadius) / 2 + 5;
            const x = this.centerX + Math.cos(midAngle) * radius;
            const y = this.centerY + Math.sin(midAngle) * radius;
            
            // Draw white background circle for readability
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            this.ctx.beginPath();
            this.ctx.arc(x, y, 12, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Draw house number
            this.ctx.fillStyle = '#2c3e50';
            this.ctx.fillText(houseNum.toString(), x, y);
        }
    }
    
    drawPlanets() {
        const planets = this.chartData.planets;
        const planetPositions = [];
        
        // Calculate all planet positions first
        for (const [name, data] of Object.entries(planets)) {
            const angle = this.calculateAngle(data.sign, data.degree);
            planetPositions.push({ name, angle, data });
        }
        
        // Sort by angle to check for overlaps
        planetPositions.sort((a, b) => a.angle - b.angle);
        
        // Adjust radii to prevent overlap
        const adjustedPositions = this.adjustPlanetPositions(planetPositions);
        
        // Store for aspect calculation
        this.planetPositions = adjustedPositions;
        
        // Draw planets
        adjustedPositions.forEach(({ name, angle, radius }) => {
            const x = this.centerX + Math.cos(angle) * radius;
            const y = this.centerY + Math.sin(angle) * radius;
            
            // Planet color based on type
            const colors = {
                'Sun': '#FDB813',
                'Moon': '#8B7355',
                'Mercury': '#4A90E2',
                'Venus': '#E74C3C',
                'Mars': '#C0392B',
                'Jupiter': '#F39C12',
                'Saturn': '#7F8C8D',
                'Uranus': '#16A085',
                'Neptune': '#2980B9',
                'Pluto': '#34495E',
                'Chiron': '#9B59B6'
            };
            
            // Draw white circle background
            this.ctx.fillStyle = '#ffffff';
            this.ctx.beginPath();
            this.ctx.arc(x, y, 14, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Draw colored border
            this.ctx.strokeStyle = colors[name] || '#2c3e50';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // Draw planet symbol
            this.ctx.fillStyle = colors[name] || '#2c3e50';
            this.ctx.font = 'bold 16px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(PLANET_SYMBOLS[name], x, y);
            
            // Draw tick mark on inner ring at exact position if displaced
            if (Math.abs(radius - this.planetRadius) > 5) {
                const tickX = this.centerX + Math.cos(angle) * this.innerRadius;
                const tickY = this.centerY + Math.sin(angle) * this.innerRadius;
                const tickX2 = this.centerX + Math.cos(angle) * (this.innerRadius - 8);
                const tickY2 = this.centerY + Math.sin(angle) * (this.innerRadius - 8);
                
                this.ctx.strokeStyle = colors[name] || '#2c3e50';
                this.ctx.lineWidth = 2;
                this.ctx.beginPath();
                this.ctx.moveTo(tickX, tickY);
                this.ctx.lineTo(tickX2, tickY2);
                this.ctx.stroke();
            }
        });
    }
    
    adjustPlanetPositions(planetPositions) {
        const minAngleDiff = 0.2; // Minimum angle between planets (radians)
        const adjusted = [];
        const layers = [this.planetRadius, this.planetRadius - 30, this.planetRadius + 30];
        
        planetPositions.forEach((planet) => {
            let bestRadius = layers[0];
            let minConflict = Infinity;
            
            // Try each layer and pick the one with least conflict
            for (const testRadius of layers) {
                let maxConflict = 0;
                
                for (const prev of adjusted) {
                    const angleDiff = Math.abs(planet.angle - prev.angle);
                    const wrappedDiff = Math.min(angleDiff, 2 * Math.PI - angleDiff);
                    
                    if (testRadius === prev.radius && wrappedDiff < minAngleDiff) {
                        maxConflict = Math.max(maxConflict, minAngleDiff - wrappedDiff);
                    }
                }
                
                if (maxConflict < minConflict) {
                    minConflict = maxConflict;
                    bestRadius = testRadius;
                }
                
                if (minConflict === 0) break;
            }
            
            adjusted.push({ ...planet, radius: bestRadius, angle: planet.angle });
        });
        
        return adjusted;
    }
    
    calculateAspectAngle(angle1, angle2) {
        // Calculate the angular difference between two planets
        let diff = Math.abs(angle1 - angle2) * 180 / Math.PI;
        // Normalize to 0-180 range
        if (diff > 180) diff = 360 - diff;
        return diff;
    }
    
    drawAspectLines() {
        if (!this.chartData.planets) return;
        
        const planetList = Object.entries(this.chartData.planets).map(([name, data]) => ({
            name,
            angle: this.calculateAngle(data.sign, data.degree)
        }));
        
        // Check all planet pairs for aspects
        for (let i = 0; i < planetList.length; i++) {
            for (let j = i + 1; j < planetList.length; j++) {
                const planet1 = planetList[i];
                const planet2 = planetList[j];
                
                const aspectAngle = this.calculateAspectAngle(planet1.angle, planet2.angle);
                
                // Check each aspect type
                for (const aspect of Object.values(this.aspects)) {
                    if (Math.abs(aspectAngle - aspect.angle) <= aspect.orb) {
                        // Draw aspect line
                        this.drawAspectLine(planet1.angle, planet2.angle, aspect);
                        break; // Only draw one aspect per pair
                    }
                }
            }
        }
    }
    
    drawAspectLine(angle1, angle2, aspect) {
        const x1 = this.centerX + Math.cos(angle1) * this.aspectRadius;
        const y1 = this.centerY + Math.sin(angle1) * this.aspectRadius;
        const x2 = this.centerX + Math.cos(angle2) * this.aspectRadius;
        const y2 = this.centerY + Math.sin(angle2) * this.aspectRadius;
        
        this.ctx.strokeStyle = aspect.color;
        this.ctx.globalAlpha = 0.6;
        this.ctx.lineWidth = 1.5;
        
        // Different line styles for different aspects
        if (aspect.name === 'Trine' || aspect.name === 'Sextile') {
            this.ctx.setLineDash([]);
        } else if (aspect.name === 'Square') {
            this.ctx.setLineDash([8, 4]);
        } else if (aspect.name === 'Opposition') {
            this.ctx.setLineDash([]);
        } else {
            this.ctx.setLineDash([4, 4]);
        }
        
        this.ctx.beginPath();
        this.ctx.moveTo(x1, y1);
        this.ctx.lineTo(x2, y2);
        this.ctx.stroke();
        
        this.ctx.setLineDash([]);
        this.ctx.globalAlpha = 1.0;
    }
    
    drawCenterInfo() {
        // Draw center circle
        this.ctx.fillStyle = '#ffffff';
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, this.centerRadius, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.strokeStyle = '#2c3e50';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // Draw ascendant marker (ASC) at 9 o'clock position
        const ascHouse = this.chartData.houses[1];
        if (ascHouse) {
            const ascAngle = this.calculateAngle(ascHouse.sign, ascHouse.degree);
            const ascX = this.centerX + Math.cos(ascAngle) * (this.centerRadius + 20);
            const ascY = this.centerY + Math.sin(ascAngle) * (this.centerRadius + 20);
            
            this.ctx.fillStyle = '#2c3e50';
            this.ctx.font = 'bold 11px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText('ASC', ascX, ascY);
        }
        
        // Draw MC marker (Midheaven) at 12 o'clock position
        const mcHouse = this.chartData.houses[10];
        if (mcHouse) {
            const mcAngle = this.calculateAngle(mcHouse.sign, mcHouse.degree);
            const mcX = this.centerX + Math.cos(mcAngle) * (this.centerRadius + 20);
            const mcY = this.centerY + Math.sin(mcAngle) * (this.centerRadius + 20);
            
            this.ctx.fillStyle = '#2c3e50';
            this.ctx.font = 'bold 11px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText('MC', mcX, mcY);
        }
    }
}

// Initialize chart when page loads
document.addEventListener('DOMContentLoaded', function() {
    const chartCanvas = document.getElementById('chartWheel');
    if (chartCanvas && window.chartData) {
        new ChartWheel('chartWheel', window.chartData);
    }
});
