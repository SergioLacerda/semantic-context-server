class BenchmarkFormatter:
    def format_report(self, report: dict) -> str:
        if not report:
            return "No data available."

        lines = ["\n--- BENCHMARK REPORT ---"]

        for k, v in report.items():
            if isinstance(v, float):
                lines.append(f"{k}: {v:.4f}")
            else:
                lines.append(f"{k}: {v}")

        return "\n".join(lines)

    def format_compare(self, results: dict) -> str:
        if not results:
            return "No comparison results."

        lines = ["\n--- BENCHMARK COMPARISON ---"]

        for mode, report in results.items():
            lines.append(f"\n[{mode.upper()}]")

            if "error" in report:
                lines.append(f"  ERROR: {report['error']}")
                continue

            for k, v in report.items():
                if isinstance(v, float):
                    lines.append(f"  {k}: {v:.4f}")
                else:
                    lines.append(f"  {k}: {v}")

        return "\n".join(lines)

    def format_strategies(self, data: dict) -> str:
        if not data:
            return "No strategy results."

        results = data.get("results", {})
        ranking = data.get("ranking", [])
        winner = data.get("winner")

        lines = ["\n--- STRATEGY COMPARISON ---"]

        # 🔹 Ranking
        if ranking:
            lines.append("\n🏆 Ranking:")
            for i, (name, report) in enumerate(ranking, start=1):
                score = self._safe_score(report)
                lines.append(f"{i}. {name} (score={score:.4f})")

        # 🔹 Winner
        if winner:
            lines.append(f"\n🥇 Winner: {winner}")

        # 🔹 Detailed results
        if results:
            lines.append("\n--- DETAILS ---")

            for name, report in results.items():
                lines.append(f"\n[{name}]")

                if "error" in report:
                    lines.append(f"  ERROR: {report['error']}")
                    continue

                for k, v in report.items():
                    if isinstance(v, float):
                        lines.append(f"  {k}: {v:.4f}")
                    else:
                        lines.append(f"  {k}: {v}")

        return "\n".join(lines)

    # ==================================================
    # INTERNAL
    # ==================================================

    def _safe_score(self, report: dict) -> float:
        if "error" in report:
            return float("inf")

        # fallback simples (mesmo do analysis)
        return float(
            report.get("p95", 0) * 0.6
            + report.get("avg", 0) * 0.3
            - report.get("throughput", 0) * 0.1
        )
