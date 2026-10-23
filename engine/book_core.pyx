
# engine/book_core.pyx

# Day 15: Cython order-book core skeleton.
# BUY = 0, SELL = 1, matching the project convention.


cdef class BookCore:
    cdef list bids
    cdef list asks
    cdef int max_price

    def __cinit__(self, int max_price=100000):
        if max_price < 1:
            raise ValueError("max_price must be positive")

        self.max_price = max_price
        self.bids = [0] * (max_price + 1)
        self.asks = [0] * (max_price + 1)

    cpdef add_order(self, int side, int price, int quantity):
        if side not in (0, 1):
            raise ValueError("side must be BUY (0) or SELL (1)")

        if price < 1 or price > self.max_price:
            raise ValueError("price is outside the supported range")

        if quantity <= 0:
            raise ValueError("quantity must be positive")

        if side == 0:
            self.bids[price] += quantity
        else:
            self.asks[price] += quantity

    cpdef best_bid(self):
        cdef int price

        for price in range(self.max_price, 0, -1):
            if self.bids[price] > 0:
                return price

        return None

    cpdef best_ask(self):
        cdef int price

        for price in range(1, self.max_price + 1):
            if self.asks[price] > 0:
                return price

        return None

    cpdef quantity_at(self, int side, int price):
        if side not in (0, 1):
            raise ValueError("side must be BUY (0) or SELL (1)")

        if price < 1 or price > self.max_price:
            raise ValueError("price is outside the supported range")

        if side == 0:
            return self.bids[price]

        return self.asks[price]
