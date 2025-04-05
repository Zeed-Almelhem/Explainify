import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { modelService, Model } from '../services/api';

export function useModels() {
  const queryClient = useQueryClient();

  const modelsQuery = useQuery<Model[]>({
    queryKey: ['models'],
    queryFn: modelService.getModels,
  });

  const uploadModelMutation = useMutation({
    mutationFn: modelService.uploadModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] });
    },
  });

  return {
    models: modelsQuery.data ?? [],
    isLoading: modelsQuery.isLoading,
    error: modelsQuery.error,
    uploadModel: uploadModelMutation.mutate,
    isUploading: uploadModelMutation.isPending,
    uploadError: uploadModelMutation.error,
  };
}
