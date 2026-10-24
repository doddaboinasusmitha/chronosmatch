
# Day 16: C-level order storage with FIFO price-time matching.

from libc.stdlib cimport calloc, free
from libc.stddef cimport size_t
from libc.stdint cimport uint64_t
from libc.stdint cimport uint32_t
from libc.stdint cimport uint8_t


cdef struct OrderNode:
    uint64_t order_id
    int quantity
    OrderNode* next


cdef class BookCore:
    cdef OrderNode** bids
    cdef OrderNode** asks
    cdef OrderNode** bid_tails
    cdef OrderNode** ask_tails
    cdef int max_price

    def __cinit__(self, int max_price=100000):
        self.bids = NULL
        self.asks = NULL
        self.bid_tails = NULL
        self.ask_tails = NULL

        if max_price < 1:
            raise ValueError("max_price must be positive")

        self.max_price = max_price

        self.bids = <OrderNode**>calloc(
            <size_t>(max_price + 1), sizeof(OrderNode*)
        )
        self.asks = <OrderNode**>calloc(
            <size_t>(max_price + 1), sizeof(OrderNode*)
        )
        self.bid_tails = <OrderNode**>calloc(
            <size_t>(max_price + 1), sizeof(OrderNode*)
        )
        self.ask_tails = <OrderNode**>calloc(
            <size_t>(max_price + 1), sizeof(OrderNode*)
        )

        if (self.bids == NULL or self.asks == NULL or
                self.bid_tails == NULL or self.ask_tails == NULL):
            raise MemoryError("Could not allocate order-book arrays")

    def __dealloc__(self):
        cdef int price
        cdef OrderNode* node
        cdef OrderNode* following

        if self.bids != NULL:
            for price in range(self.max_price + 1):
                node = self.bids[price]
                while node != NULL:
                    following = node.next
                    free(node)
                    node = following
            free(self.bids)

        if self.asks != NULL:
            for price in range(self.max_price + 1):
                node = self.asks[price]
                while node != NULL:
                    following = node.next
                    free(node)
                    node = following
            free(self.asks)

        if self.bid_tails != NULL:
            free(self.bid_tails)

        if self.ask_tails != NULL:
            free(self.ask_tails)

    cpdef add_order(
        self, int side, int price, int quantity,
        unsigned long long order_id=0
    ):
        cdef OrderNode** opposite
        cdef OrderNode** own
        cdef OrderNode** own_tails
        cdef OrderNode* resting
        cdef OrderNode* incoming_node
        cdef int best_price
        cdef int remaining = quantity
        cdef int fill_quantity
        cdef list trades = []
        cdef dict trade

        if side not in (0, 1):
            raise ValueError("side must be BUY (0) or SELL (1)")
        if price < 1 or price > self.max_price:
            raise ValueError("price is outside the supported range")
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        if side == 0:
            opposite = self.asks
            own = self.bids
            own_tails = self.bid_tails
        else:
            opposite = self.bids
            own = self.asks
            own_tails = self.ask_tails

        while remaining > 0:
            best_price = -1

            if side == 0:
                for best_price in range(1, self.max_price + 1):
                    if opposite[best_price] != NULL:
                        break
                else:
                    best_price = -1
            else:
                for best_price in range(self.max_price, 0, -1):
                    if opposite[best_price] != NULL:
                        break
                else:
                    best_price = -1

            if best_price == -1:
                break

            if side == 0 and best_price > price:
                break
            if side == 1 and best_price < price:
                break

            resting = opposite[best_price]
            fill_quantity = remaining
            if resting.quantity < fill_quantity:
                fill_quantity = resting.quantity

            if side == 0:
                trade = {
                    "buy_order_id": order_id,
                    "sell_order_id": resting.order_id,
                    "price": best_price,
                    "quantity": fill_quantity,
                }
            else:
                trade = {
                    "buy_order_id": resting.order_id,
                    "sell_order_id": order_id,
                    "price": best_price,
                    "quantity": fill_quantity,
                }

            trades.append(trade)
            remaining -= fill_quantity
            resting.quantity -= fill_quantity

            if resting.quantity == 0:
                opposite[best_price] = resting.next
                if opposite[best_price] == NULL:
                    if side == 0:
                        self.ask_tails[best_price] = NULL
                    else:
                        self.bid_tails[best_price] = NULL
                free(resting)

        if remaining > 0:
            incoming_node = <OrderNode*>calloc(
                1, sizeof(OrderNode)
            )
            if incoming_node == NULL:
                raise MemoryError("Could not allocate order node")

            incoming_node.order_id = order_id
            incoming_node.quantity = remaining
            incoming_node.next = NULL

            if own[price] == NULL:
                own[price] = incoming_node
                own_tails[price] = incoming_node
            else:
                own_tails[price].next = incoming_node
                own_tails[price] = incoming_node

        return trades

    cpdef best_bid(self):
        cdef int price
        for price in range(self.max_price, 0, -1):
            if self.bids[price] != NULL:
                return price
        return None

    cpdef best_ask(self):
        cdef int price
        for price in range(1, self.max_price + 1):
            if self.asks[price] != NULL:
                return price
        return None

    cpdef quantity_at(self, int side, int price):
        cdef OrderNode* node
        cdef long long total = 0

        if side not in (0, 1):
            raise ValueError("side must be BUY (0) or SELL (1)")
        if price < 1 or price > self.max_price:
            raise ValueError("price is outside the supported range")

        if side == 0:
            node = self.bids[price]
        else:
            node = self.asks[price]

        while node != NULL:
            total += node.quantity
            node = node.next

        return total
