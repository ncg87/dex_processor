# Uniswap V3 Queries #
def get_uniswap_v3_query():
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
def get_uniswap_v3_tokens_query():
    """Fetch all tokens from the specified DEX subgraph."""
    return """
    query ($first: Int!, $skip: Int!) {
        tokens(first: $first, skip: $skip, orderBy: volumeUSD, orderDirection: desc) {
            id
            symbol
            name
        }
    }
    """
    
    
# Uniswap V2 Queries #
def get_uniswap_v2_query():
    """
    Query to fetch transactions within a time period from Uniswap V2.
    """
    return """
    query GetSwapsBurnsMints($startTimestamp: Int!, $endTimestamp: Int!, $skip: Int!) {
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

            # Swap events
            swaps {
            id
            transaction {
                id
            }
            timestamp
            pair {
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
            }
            sender
            from
            amount0In
            amount1In
            amount0Out
            amount1Out
            to
            logIndex
            amountUSD
            }

            # Mint events
            mints {
            id
            transaction {
                id
            }
            timestamp
            pair {
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
            }
            sender
            to
            liquidity
            amount0
            amount1
            logIndex
            amountUSD
            feeTo
            feeLiquidity
            }

            # Burn events
            burns {
            id
            transaction {
                id
            }
            timestamp
            pair {
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
            }
            liquidity
            sender
            amount0
            amount1
            to
            logIndex
            amountUSD
            feeTo
            feeLiquidity
            }
        }
    }
    """
