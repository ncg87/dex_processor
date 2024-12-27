def get_transactions_query():
    """
    Query to fetch transactions within a time period.
    """
    return """
        query GetTransactions($startTimestamp: Int!, $endTimestamp: Int!, $skip: Int!) {
        transactions(
            first: 1000
            skip: $skip
            where: { timestamp_gte: $startTimestamp, timestamp_lte: $endTimestamp }
            orderBy: timestamp
            orderDirection: asc
        ) {
            id
            blockNumber
            timestamp
            gasUsed
            gasPrice
            
            # Swap events
            swaps {
            id
            timestamp
            pool {
                id
                token0 {
                id
                symbol
                decimals
                }
                token1 {
                id
                symbol
                decimals
                }
                feeTier
                liquidity
                sqrtPrice
                token0Price
                token1Price
            }
            sender
            recipient
            origin
            amount0
            amount1
            amountUSD
            sqrtPriceX96
            tick
            logIndex
            }
            
            # Mint events
            mints {
            id
            timestamp
            pool {
                id
                token0 {
                id
                symbol
                decimals
                }
                token1 {
                id
                symbol
                decimals
                }
                feeTier
                liquidity
                sqrtPrice
                token0Price
                token1Price
            }
            token0
            token1
            owner
            sender
            origin
            amount
            amount0
            amount1
            amountUSD
            tickLower
            tickUpper
            logIndex
            }
            
            # Burn events
            burns {
            id
            transaction {
                id
            }
            pool {
                id
                token0 {
                id
                symbol
                decimals
                }
                token1 {
                id
                symbol
                decimals
                }
                feeTier
                liquidity
                sqrtPrice
                token0Price
                token1Price
            }
            token0
            token1
            owner
            origin
            amount
            amount0
            amount1
            amountUSD
            tickLower
            tickUpper
            logIndex
            }
            
            # Flash events
            flashed {
            id
            timestamp
            pool {
                id
                token0 {
                id
                symbol
                decimals
                }
                token1 {
                id
                symbol
                decimals
                }
                feeTier
                liquidity
                sqrtPrice
                token0Price
                token1Price
            }
            sender
            recipient
            amount0
            amount1
            amountUSD
            amount0Paid
            amount1Paid
            logIndex
            }
            
            # Collect events
            collects {
            id
            timestamp
            pool {
                id
                token0 {
                id
                symbol
                decimals
                }
                token1 {
                id
                symbol
                decimals
                }
                feeTier
                liquidity
                sqrtPrice
                token0Price
                token1Price
            }
            owner
            amount0
            amount1
            amountUSD
            tickLower
            tickUpper
            logIndex
            }
        }
        }
    """