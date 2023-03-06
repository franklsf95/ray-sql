import os

import ray
from raysql.context import RaySqlContext
from raysql.worker import Worker

DATA_DIR = "/home/ubuntu/tpch/sf1-parquet"
# DATA_DIR = "/home/ubuntu/sf10-parquet"

ray.init()


def setup_context(use_ray_shuffle: bool) -> RaySqlContext:
    num_workers = 2
    # num_workers = os.cpu_count()
    workers = [Worker.remote() for _ in range(num_workers)]
    ctx = RaySqlContext.remote(workers, use_ray_shuffle)
    register_tasks = []
    register_tasks.append(ctx.register_csv.remote("tips", "examples/tips.csv", True))
    for table in [
        "customer",
        "lineitem",
        "nation",
        "orders",
        "part",
        "partsupp",
        "region",
        "supplier",
    ]:
        register_tasks.append(
            ctx.register_parquet.remote(table, f"{DATA_DIR}/{table}.parquet")
        )
    return ctx


def load_query(n: int) -> str:
    with open(f"testdata/queries/q{n}.sql") as fin:
        return fin.read()


def tpchq(ctx: RaySqlContext, q: int = 1):
    sql = load_query(q)
    result_set = ray.get(ctx.sql.remote(sql))
    print(result_set[0])


use_ray_shuffle = True
ctx = setup_context(use_ray_shuffle)
tpchq(ctx)
