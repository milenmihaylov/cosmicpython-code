from datetime import date, timedelta

import pytest

from model import Batch, OrderLine, allocate, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=7)

def test_prefers_current_stock_batches_to_shipment():
    in_stock_batch = Batch("in-stock-batch", "clock", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "clock", 100, eta=tomorrow)
    line = OrderLine("oref", "clock", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefers_earlier_batches():
    earliest = Batch("speed", "spoon", 100, eta=today)
    medium = Batch("normal", "spoon", 100, eta=tomorrow)
    latest = Batch("slow", "spoon", 100, eta=today)
    line = OrderLine("order1", "spoon", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100

def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference

def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "clock", 10, eta=today)
    allocate(OrderLine('order1', 'clock', 10), [batch])

    with pytest.raises(OutOfStock, match='clock'):
        allocate(OrderLine('order2', 'clock', 1), [batch])
