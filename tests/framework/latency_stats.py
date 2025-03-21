import statistics


def analyze_2_data_feeds_latency(data_feeds_latencies: dict, percentiles: list):
    results = {
        "latency_diffs": [],
        "a_latencies": [],
        "b_latencies": [],
        "a_wins": 0,
        "b_wins": 0,
        "total_matches": 0
    }

    for trade_id, record in data_feeds_latencies.items():
        if 'A' in record and 'B' in record:
            a_time = record['A']
            b_time = record['B']

            diff_ms = (a_time - b_time) * 1000

            results["latency_diffs"].append(diff_ms)
            results["a_latencies"].append(a_time * 1000)
            results["b_latencies"].append(b_time * 1000)

            if a_time < b_time:
                results["a_wins"] += 1
            elif b_time < a_time:
                results["b_wins"] += 1

            results["total_matches"] += 1
        else:
            pass

    # Calculate stats
    if results["a_latencies"]:
        results["mean_a"] = round(statistics.mean(results["a_latencies"]), 2)
        results["percentiles_a"] = calculate_percentiles(results["a_latencies"], percentiles)
    else:
        results["mean_a"] = 0
        results["percentiles_a"] = {}

    if results["b_latencies"]:
        results["mean_b"] = round(statistics.mean(results["b_latencies"]), 2)
        results["percentiles_b"] = calculate_percentiles(results["b_latencies"], percentiles)
    else:
        results["mean_b"] = 0
        results["percentiles_b"] = {}

    if results["latency_diffs"]:
        results["mean_diff"] = round(statistics.mean(results["latency_diffs"]), 2)
        results["diff_percentiles"] = calculate_percentiles(results["latency_diffs"], percentiles)
    else:
        results["mean_diff"] = 0
        results["diff_percentiles"] = {}

    if results["total_matches"] > 0:
        results["a_win_pct"] = round((results["a_wins"] / results["total_matches"]) * 100, 2)
        results["b_win_pct"] = round((results["b_wins"] / results["total_matches"]) * 100, 2)
    else:
        results["a_win_pct"] = 0
        results["b_win_pct"] = 0

    return results


def calculate_percentiles(data: list, percentiles: list):
    return {p: round(statistics.quantiles(data, n=100)[p - 1], 2) for p in percentiles}


def report_data_feeds_latency_stats(feeds_stats: dict, logger):
    # Feed A stats
    logger.info(f"Feed A:")
    logger.info(f"Latency: mean={feeds_stats['mean_a']}ms")
    logger.info(f"Latency Percentiles (ms): {feeds_stats['percentiles_a']}\n")

    # Feed B stats
    logger.info(f"Feed B:")
    logger.info(f"Latency: mean={feeds_stats['mean_b']}ms")
    logger.info(f"Latency Percentiles (ms): {feeds_stats['percentiles_b']}\n")

    # Latency difference stats
    logger.info(f"Latency Difference (A-B):")
    logger.info(f"Mean diff = {feeds_stats['mean_diff']}ms")
    logger.info(f"Diff Percentiles (ms): {feeds_stats['diff_percentiles']}\n")

    # Summary with percentages
    logger.info("Result:")
    logger.info(f"Feed A has lower latency in {feeds_stats['a_win_pct']}% of the cases!")
    logger.info(f"Feed B has lower latency in {feeds_stats['b_win_pct']}% of the cases!")

