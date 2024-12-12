def _get_available_context_size(self, num_prompt_tokens: int) -> int:
    # 确保 num_prompt_tokens 不超过允许的最大值
    max_context_size = self.max_context_size  # 假设这是定义的最大值
    available_context_size = max_context_size - num_prompt_tokens
    if available_context_size < 0:
        raise ValueError(
            f"Calculated available context size {available_context_size} was not non-negative."
        )
    return available_context_size 