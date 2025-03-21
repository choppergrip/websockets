import statistics

def analyze_2_data_feeds_latency(data_feeds_latencies: dict, percentiles: list):
    """
    Analyzes and compares the latency of two data feeds (Feed A and Feed B) across multiple records.

    The function processes a dictionary containing latency timestamps for two data feeds
    and calculates several statistics, including:

    - Mean latencies for Feed A and Feed B (in milliseconds).
    - Latency percentiles for both feeds.
    - Mean latency difference (A - B) and percentiles of the differences.
    - Win percentages indicating how often each feed had lower latency.

    Args:
        data_feeds_latencies (dict): A dictionary where each key is a unique trade ID and each value
                                     is a dict with keys:
                                     - 'A' (float): Timestamp of Feed A (in seconds).
                                     - 'B' (float): Timestamp of Feed B (in seconds).
        percentiles (list): A list of integers representing desired percentiles to compute
                            (e.g., [50, 90, 95]).

    Returns:
        dict: A dictionary containing:
            - 'latency_diffs' (list): List of latency differences (A - B) in milliseconds.
            - 'a_latencies' (list): List of Feed A latencies in milliseconds.
            - 'b_latencies' (list): List of Feed B latencies in milliseconds.
            - 'a_wins' (int): Number of times Feed A had lower latency.
            - 'b_wins' (int): Number of times Feed B had lower latency.
            - 'total_matches' (int): Total number of comparisons made.
            - 'mean_a' (float): Mean latency for Feed A in milliseconds.
            - 'percentiles_a' (dict): Calculated percentiles for Feed A latencies.
            - 'mean_b' (float): Mean latency for Feed B in milliseconds.
            - 'percentiles_b' (dict): Calculated percentiles for Feed B latencies.
            - 'mean_diff' (float): Mean latency difference (A - B) in milliseconds.
            - 'diff_percentiles' (dict): Calculated percentiles for the latency differences.
            - 'a_win_pct' (float): Percentage of cases where Feed A had lower latency.
            - 'b_win_pct' (float): Percentage of cases where Feed B had lower latency.

    Notes:
        - Latency values are converted from seconds to milliseconds before statistical calculations.
        - Only non-equal latency cases contribute to win percentages (ties are ignored).
    """
    results = {
        "latency_diffs": [],
        "a_latencies": [],
        "b_latencies": [],
        "a_wins": 0,
        "b_wins": 0,
        "total_matches": 0
    }

    for _, record in data_feeds_latencies.items():
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

    results["total_matches"] = results["a_wins"] + results["b_wins"]

    # Calculate stats assuming data always exists
    results["mean_a"] = round(statistics.mean(results["a_latencies"]), 2)
    results["percentiles_a"] = calculate_percentiles(results["a_latencies"], percentiles)

    results["mean_b"] = round(statistics.mean(results["b_latencies"]), 2)
    results["percentiles_b"] = calculate_percentiles(results["b_latencies"], percentiles)

    results["mean_diff"] = round(statistics.mean(results["latency_diffs"]), 2)
    results["diff_percentiles"] = calculate_percentiles(results["latency_diffs"], percentiles)

    results["a_win_pct"] = round((results["a_wins"] / results["total_matches"]) * 100, 2)
    results["b_win_pct"] = round((results["b_wins"] / results["total_matches"]) * 100, 2)

    return results


def calculate_percentiles(data: list, percentiles: list):
    """
    Calculates specified percentiles from a dataset.

    This function computes the requested percentiles from the provided data list
    using a quantile-based approach (percentile ranks from 1 to 99).

    Args:
        data (list): A list of numerical values to compute percentiles from.
        percentiles (list): A list of integers representing desired percentiles
                            (e.g., [50, 90, 95]) where each value should be between 1 and 99.

    Returns:
        dict: A dictionary where keys are the requested percentiles and values are the
              corresponding percentile values rounded to 2 decimal places.
    """
    return {p: round(statistics.quantiles(data, n=100)[p - 1], 2) for p in percentiles}


def report_data_feeds_latency_stats(feeds_stats: dict, logger):
    """
    Logs latency statistics for two data feeds (Feed A and Feed B) and their latency differences.

    The function takes in a dictionary containing statistical metrics for two data feeds
    and logs the following information using the provided logger:

    - Mean latency and latency percentiles for Feed A.
    - Mean latency and latency percentiles for Feed B.
    - Mean latency difference (Feed A - Feed B) and its percentiles.
    - Summary showing the percentage of cases where Feed A or Feed B has lower latency.

    Args:
        feeds_stats (dict): A dictionary containing the following keys:
            - 'mean_a' (float): Mean latency for Feed A in milliseconds.
            - 'percentiles_a' (dict or list): Latency percentiles for Feed A.
            - 'mean_b' (float): Mean latency for Feed B in milliseconds.
            - 'percentiles_b' (dict or list): Latency percentiles for Feed B.
            - 'mean_diff' (float): Mean latency difference (Feed A - Feed B) in milliseconds.
            - 'diff_percentiles' (dict or list): Percentiles for the latency difference.
            - 'a_win_pct' (float): Percentage of cases where Feed A has lower latency.
            - 'b_win_pct' (float): Percentage of cases where Feed B has lower latency.
        logger: A logging instance to output the formatted statistics.

    Returns:
        None
    """
    # Feed A stats
    logger.info("Feed A:")
    logger.info(f"Latency: mean={feeds_stats['mean_a']}ms")
    logger.info(f"Latency Percentiles (ms): {feeds_stats['percentiles_a']}\n")

    # Feed B stats
    logger.info("Feed B:")
    logger.info(f"Latency: mean={feeds_stats['mean_b']}ms")
    logger.info(f"Latency Percentiles (ms): {feeds_stats['percentiles_b']}\n")

    # Latency difference stats
    logger.info("Latency Difference (A-B):")
    logger.info(f"Mean diff = {feeds_stats['mean_diff']}ms")
    logger.info(f"Diff Percentiles (ms): {feeds_stats['diff_percentiles']}\n")

    # Summary with percentages
    logger.info("Result:")
    logger.info(f"Feed A has lower latency in {feeds_stats['a_win_pct']}% of the cases!")
    logger.info(f"Feed B has lower latency in {feeds_stats['b_win_pct']}% of the cases!")
