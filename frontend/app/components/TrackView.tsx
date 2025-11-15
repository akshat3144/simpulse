"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { Car } from "../types/race";

interface TrackViewProps {
  cars: Car[];
  trackLength: number;
}

export default function TrackView({
  cars,
  trackLength = 2500,
}: TrackViewProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || cars.length === 0) return;

    const svg = d3.select(svgRef.current);
    const width = 900;
    const height = 400;
    const margin = 50;

    // Clear previous content
    svg.selectAll("*").remove();

    // Setup SVG
    svg.attr("width", width).attr("height", height);

    // Define track path (realistic Formula E street circuit)
    const centerX = width / 2;
    const centerY = height / 2;
    const mainRadius = 140;

    // Create a realistic street circuit path
    const trackPath = `
      M ${centerX - 200},${centerY}
      L ${centerX - 150},${centerY}
      Q ${centerX - 100},${centerY} ${centerX - 100},${centerY - 50}
      L ${centerX - 100},${centerY - 80}
      Q ${centerX - 100},${centerY - 100} ${centerX - 80},${centerY - 100}
      L ${centerX + 80},${centerY - 100}
      Q ${centerX + 100},${centerY - 100} ${centerX + 100},${centerY - 80}
      L ${centerX + 100},${centerY - 20}
      Q ${centerX + 100},${centerY} ${centerX + 120},${centerY}
      L ${centerX + 180},${centerY}
      Q ${centerX + 200},${centerY} ${centerX + 200},${centerY + 20}
      L ${centerX + 200},${centerY + 80}
      Q ${centerX + 200},${centerY + 100} ${centerX + 180},${centerY + 100}
      L ${centerX - 80},${centerY + 100}
      Q ${centerX - 100},${centerY + 100} ${centerX - 100},${centerY + 80}
      L ${centerX - 100},${centerY + 20}
      Q ${centerX - 100},${centerY} ${centerX - 120},${centerY}
      L ${centerX - 200},${centerY}
    `;

    // Draw track background (wider gray area)
    svg
      .append("path")
      .attr("d", trackPath)
      .attr("fill", "none")
      .attr("stroke", "#2a2a2a")
      .attr("stroke-width", 30);

    // Draw track surface
    svg
      .append("path")
      .attr("d", trackPath)
      .attr("fill", "none")
      .attr("stroke", "#444")
      .attr("stroke-width", 24);

    // Draw track center line (dashed)
    svg
      .append("path")
      .attr("d", trackPath)
      .attr("fill", "none")
      .attr("stroke", "#666")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "10,10");

    // Get path element for calculations
    const pathElement = svg
      .append("path")
      .attr("d", trackPath)
      .node() as SVGPathElement;

    const pathLength = pathElement?.getTotalLength() || trackLength;

    // Start/Finish line
    const startPoint = pathElement?.getPointAtLength(0);
    if (startPoint) {
      // Start line
      svg
        .append("line")
        .attr("x1", startPoint.x - 12)
        .attr("y1", startPoint.y - 12)
        .attr("x2", startPoint.x - 12)
        .attr("y2", startPoint.y + 12)
        .attr("stroke", "#00ff00")
        .attr("stroke-width", 4);

      svg
        .append("text")
        .attr("x", startPoint.x - 12)
        .attr("y", startPoint.y - 20)
        .attr("text-anchor", "middle")
        .attr("fill", "#00ff00")
        .attr("font-size", "12px")
        .attr("font-weight", "bold")
        .text("START/FINISH");

      // Checkered pattern
      for (let i = 0; i < 6; i++) {
        svg
          .append("rect")
          .attr("x", startPoint.x - 14)
          .attr("y", startPoint.y - 12 + i * 4)
          .attr("width", 4)
          .attr("height", 4)
          .attr("fill", i % 2 === 0 ? "white" : "black");
      }
    }

    // Sector markers (every 1/4 of track)
    for (let sector = 1; sector < 4; sector++) {
      const sectorPoint = pathElement?.getPointAtLength(
        (pathLength * sector) / 4
      );
      if (sectorPoint) {
        svg
          .append("circle")
          .attr("cx", sectorPoint.x)
          .attr("cy", sectorPoint.y)
          .attr("r", 3)
          .attr("fill", "#ff6600")
          .attr("opacity", 0.6);

        svg
          .append("text")
          .attr("x", sectorPoint.x)
          .attr("y", sectorPoint.y - 10)
          .attr("text-anchor", "middle")
          .attr("fill", "#ff6600")
          .attr("font-size", "10px")
          .text(`S${sector}`);
      }
    }

    // Sort cars by position
    const activeCars = cars.filter((car) => car.is_active);
    const sortedCars = [...activeCars].sort(
      (a, b) => b.total_distance - a.total_distance
    );

    // Draw cars on the track
    const carGroup = svg.append("g");

    sortedCars.forEach((car, index) => {
      // Calculate position on path
      const normalizedDistance = (car.lap_distance % trackLength) / trackLength;
      const distanceOnPath = normalizedDistance * pathLength;
      const point = pathElement?.getPointAtLength(distanceOnPath);

      if (point) {
        // Car color (leader is gold)
        const color =
          index === 0 ? "#FFD700" : d3.schemeCategory10[car.id % 10];

        // Car circle (larger)
        carGroup
          .append("circle")
          .attr("cx", point.x)
          .attr("cy", point.y)
          .attr("r", 8)
          .attr("fill", color)
          .attr("stroke", "black")
          .attr("stroke-width", 2)
          .style("cursor", "pointer")
          .append("title")
          .text(
            `${car.driver_name}\nPosition: ${car.position}\nLap: ${
              car.current_lap
            }\nSpeed: ${car.speed_kmh.toFixed(
              1
            )} km/h\nBattery: ${car.battery_percentage.toFixed(1)}%`
          );

        // Position number inside car
        carGroup
          .append("text")
          .attr("x", point.x)
          .attr("y", point.y + 4)
          .attr("text-anchor", "middle")
          .attr("fill", "black")
          .attr("font-size", "10px")
          .attr("font-weight", "bold")
          .text(car.position);

        // Attack mode indicator
        if (car.attack_mode_active) {
          carGroup
            .append("text")
            .attr("x", point.x + 12)
            .attr("y", point.y - 8)
            .attr("text-anchor", "middle")
            .attr("font-size", "16px")
            .text("⚡");
        }
      }
    });

    // Title
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .attr("font-size", "16px")
      .attr("font-weight", "bold")
      .text("🏁 Live Track View - Street Circuit");

    // Legend
    svg
      .append("text")
      .attr("x", 20)
      .attr("y", height - 10)
      .attr("fill", "#888")
      .attr("font-size", "10px")
      .text(`${activeCars.length} cars racing • Track: ${trackLength}m`);
  }, [cars, trackLength]);

  return (
    <div className="bg-gray-900 rounded-lg p-6 shadow-lg">
      <svg ref={svgRef}></svg>
    </div>
  );
}
