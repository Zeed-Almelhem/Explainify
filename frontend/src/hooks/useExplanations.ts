import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { explanationService, Explanation } from '../services/api';

export function useExplanations(modelId?: string) {
  const queryClient = useQueryClient();

  const explanationsQuery = useQuery<Explanation[]>({
    queryKey: ['explanations', modelId],
    queryFn: () => explanationService.getExplanations(modelId),
    enabled: modelId !== undefined,
  });

  const generateExplanationMutation = useMutation({
    mutationFn: explanationService.generateExplanation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['explanations', modelId] });
    },
  });

  return {
    explanations: explanationsQuery.data ?? [],
    isLoading: explanationsQuery.isLoading,
    error: explanationsQuery.error,
    generateExplanation: generateExplanationMutation.mutate,
    isGenerating: generateExplanationMutation.isPending,
    generateError: generateExplanationMutation.error,
  };
}
