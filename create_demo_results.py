from pathlib import Path
import random
import polars as pl

from ethos.inference.constants import Reason
from ethos.constants import SpecialToken as ST  # <-- important

random.seed(42)

out_dir = Path("results/READMISSION/demo_run")
out_dir.mkdir(parents=True, exist_ok=True)

N_SAMPLES = 50
N_ROLLOUTS = 5

rows = []
for data_idx in range(N_SAMPLES):
    patient_id = 1000 + data_idx

    # Make sure we have BOTH classes in y_true:
    # Positive class: expected=ADMISSION and true_token_time <= 30
    # Negative class: expected=NONE or true_token_time > 30
    is_positive = (data_idx < N_SAMPLES // 2)

    if is_positive:
        expected_token = str(ST.ADMISSION)  # exact token string
        true_time_days = random.choice([5, 10, 15, 20, 25, 30])  # <= 30
    else:
        expected_token = "NONE"
        true_time_days = random.choice([40, 60, 90])  # > 30

    for rep in range(N_ROLLOUTS):
        stop_reason = Reason.GOT_TOKEN.value if rep == 0 else Reason.TIME_LIMIT.value

        # Predicted token: make positives likely for positive samples
        if is_positive:
            actual_token = str(ST.ADMISSION) if random.random() < 0.75 else "NONE"
        else:
            actual_token = str(ST.ADMISSION) if random.random() < 0.15 else "NONE"

        token_time_days = random.choice([3, 7, 12, 18, 25])

        rows.append({
            "data_idx": data_idx,
            "patient_id": patient_id,
            "stop_reason": stop_reason,
            "expected": expected_token,
            "actual": actual_token,
            "token_dist": float(random.randint(1, 6)),
            "true_token_dist": float(random.randint(1, 6)),
            "token_time_days": token_time_days,
            "true_token_time_days": true_time_days,
        })

df = pl.DataFrame(rows).with_columns(
    (pl.col("token_time_days") * pl.duration(days=1)).alias("token_time"),
    (pl.col("true_token_time_days") * pl.duration(days=1)).alias("true_token_time"),
).drop(["token_time_days", "true_token_time_days"])

fp = out_dir / "demo.parquet"
df.write_parquet(fp)

print("Wrote:", fp.resolve())
print("Rows:", df.height, "Cols:", df.width)
print("Expected unique:", df["expected"].unique())
print("Actual unique:", df["actual"].unique())
stats = df.select(
    (pl.col("true_token_time") / pl.duration(days=1)).min().alias("min_days"),
    (pl.col("true_token_time") / pl.duration(days=1)).max().alias("max_days"),
)
print("true_token_time min/max days:\n", stats)

