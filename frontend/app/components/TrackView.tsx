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
    const height = 200;
    const margin = { left: 50, right: 50, top: 30, bottom: 30 };
    const trackY = height / 2;

    // Clear previous content
    svg.selectAll("*").remove();

    // Setup SVG
    svg.attr("width", width).attr("height", height);

    // Draw track
    const trackStart = margin.left;
    const trackEnd = width - margin.right;

    // Track line
    svg
      .append("line")
      .attr("x1", trackStart)
      .attr("y1", trackY)
      .attr("x2", trackEnd)
      .attr("y2", trackY)
      .attr("stroke", "#444")
      .attr("stroke-width", 8);

    // Start line
    svg
      .append("line")
      .attr("x1", trackStart)
      .attr("y1", trackY - 25)
      .attr("x2", trackStart)
      .attr("y2", trackY + 25)
      .attr("stroke", "#00ff00")
      .attr("stroke-width", 4);

    svg
      .append("text")
      .attr("x", trackStart)
      .attr("y", trackY - 35)
      .attr("text-anchor", "middle")
      .attr("fill", "#00ff00")
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .text("START");

    // Finish line (checkered)
    for (let i = 0; i < 5; i++) {
      svg
        .append("rect")
        .attr("x", trackEnd - 2)
        .attr("y", trackY - 25 + i * 10)
        .attr("width", 4)
        .attr("height", 5)
        .attr("fill", i % 2 === 0 ? "black" : "white");
    }

    svg
      .append("text")
      .attr("x", trackEnd)
      .attr("y", trackY - 35)
      .attr("text-anchor", "middle")
      .attr("fill", "#ff0000")
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .text("FINISH");

    // Scale for car positions
    const xScale = d3
      .scaleLinear()
      .domain([0, trackLength])
      .range([trackStart, trackEnd]);

    // Sort cars by position
    const activeCars = cars.filter((car) => car.is_active);
    const sortedCars = [...activeCars].sort(
      (a, b) => b.total_distance - a.total_distance
    );

    // Draw cars
    const carGroup = svg.append("g");

    sortedCars.forEach((car, index) => {
      const x = xScale(car.lap_distance);
      const y = trackY + (index - sortedCars.length / 2) * 3;

      // Car color (leader is gold)
      const color = index === 0 ? "#FFD700" : d3.schemeCategory10[car.id % 10];

      // Car circle
      carGroup
        .append("circle")
        .attr("cx", x)
        .attr("cy", y)
        .attr("r", 6)
        .attr("fill", color)
        .attr("stroke", "black")
        .attr("stroke-width", 1.5)
        .style("cursor", "pointer")
        .append("title")
        .text(
          `${car.driver_name}\nPosition: ${car.position}\nLap: ${
            car.current_lap
          }\nSpeed: ${car.speed_kmh.toFixed(
            1
          )} km/h\nBattery: ${car.battery_percentage.toFixed(1)}%`
        );

      // Attack mode indicator
      if (car.attack_mode_active) {
        carGroup
          .append("text")
          .attr("x", x)
          .attr("y", y - 12)
          .attr("text-anchor", "middle")
          .attr("font-size", "14px")
          .text("⚡");
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
      .text("Live Track View");
  }, [cars, trackLength]);

  return (
    <div className="bg-gray-900 rounded-lg p-6 shadow-lg">
      <svg ref={svgRef}></svg>
    </div>
  );
}
