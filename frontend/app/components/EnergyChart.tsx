"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { Car } from "../types/race";

interface EnergyChartProps {
  cars: Car[];
}

export default function EnergyChart({ cars }: EnergyChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || cars.length === 0) return;

    const svg = d3.select(svgRef.current);
    const width = 450;
    const height = 300;
    const margin = { top: 40, right: 30, bottom: 50, left: 60 };

    // Clear previous content
    svg.selectAll("*").remove();

    svg.attr("width", width).attr("height", height);

    // Get top 5 cars by position
    const topCars = [...cars]
      .filter((car) => car.is_active)
      .sort((a, b) => a.position - b.position)
      .slice(0, 5);

    // Scales
    const xScale = d3
      .scaleBand()
      .domain(topCars.map((car) => car.driver_name))
      .range([margin.left, width - margin.right])
      .padding(0.3);

    const yScale = d3
      .scaleLinear()
      .domain([0, 100])
      .range([height - margin.bottom, margin.top]);

    // Color scale
    const colorScale = d3
      .scaleSequential(d3.interpolateRdYlGn)
      .domain([0, 100]);

    // Bars
    svg
      .selectAll("rect")
      .data(topCars)
      .enter()
      .append("rect")
      .attr("x", (d) => xScale(d.driver_name)!)
      .attr("y", (d) => yScale(d.battery_percentage))
      .attr("width", xScale.bandwidth())
      .attr(
        "height",
        (d) => height - margin.bottom - yScale(d.battery_percentage)
      )
      .attr("fill", (d) => colorScale(d.battery_percentage))
      .attr("stroke", "black")
      .attr("stroke-width", 1)
      .append("title")
      .text((d) => `${d.driver_name}: ${d.battery_percentage.toFixed(1)}%`);

    // Battery percentage text on bars
    svg
      .selectAll("text.value")
      .data(topCars)
      .enter()
      .append("text")
      .attr("class", "value")
      .attr("x", (d) => xScale(d.driver_name)! + xScale.bandwidth() / 2)
      .attr("y", (d) => yScale(d.battery_percentage) - 5)
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .text((d) => `${d.battery_percentage.toFixed(0)}%`);

    // X axis
    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(xScale))
      .selectAll("text")
      .attr("fill", "white")
      .attr("transform", "rotate(-20)")
      .style("text-anchor", "end")
      .style("font-size", "11px");

    // Y axis
    svg
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(
        d3
          .axisLeft(yScale)
          .ticks(5)
          .tickFormat((d) => `${d}%`)
      )
      .selectAll("text")
      .attr("fill", "white");

    // Axis lines
    svg.selectAll(".domain, .tick line").attr("stroke", "#666");

    // Title
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .attr("font-size", "16px")
      .attr("font-weight", "bold")
      .text("🔋 Battery Energy (Top 5)");

    // Grid lines
    svg
      .append("g")
      .attr("class", "grid")
      .attr("transform", `translate(${margin.left},0)`)
      .call(
        d3
          .axisLeft(yScale)
          .ticks(5)
          .tickSize(-(width - margin.left - margin.right))
          .tickFormat(() => "")
      )
      .selectAll("line")
      .attr("stroke", "#333")
      .attr("stroke-dasharray", "2,2");
  }, [cars]);

  return (
    <div className="bg-gray-900 rounded-lg p-4 shadow-lg">
      <svg ref={svgRef}></svg>
    </div>
  );
}
