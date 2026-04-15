import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { 
  HelpCircle, 
  CheckCircle, 
  AlertTriangle, 
  Lightbulb,
  BookOpen,
  BarChart3
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'sonner';
import { getDecisionSupport, getSupportedTasks } from '@/lib/api';
import type { DecisionRequest, Recommendation } from '@/types';

function RecommendationCard({ 
  recommendation, 
  isPrimary 
}: { 
  recommendation: Recommendation; 
  isPrimary: boolean;
}) {
  return (
    <Card className={isPrimary ? 'border-primary' : ''}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{recommendation.approach_family}</CardTitle>
            <CardDescription>{recommendation.description}</CardDescription>
          </div>
          <Badge variant={isPrimary ? 'default' : 'secondary'}>
            {(recommendation.suitability_score * 100).toFixed(0)}% match
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="text-sm font-medium mb-2">Recommended Models</h4>
          <div className="flex flex-wrap gap-2">
            {recommendation.recommended_models.map((model, i) => (
              <Badge key={i} variant="outline">{model}</Badge>
            ))}
          </div>
        </div>

        <div>
          <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
            <CheckCircle className="h-4 w-4 text-green-600" />
            Strengths
          </h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            {recommendation.strengths.map((strength, i) => (
              <li key={i}>{strength}</li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            Limitations
          </h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            {recommendation.limitations.map((limitation, i) => (
              <li key={i}>{limitation}</li>
            ))}
          </ul>
        </div>

        <div className="bg-muted p-3 rounded-lg">
          <h4 className="text-sm font-medium mb-1 flex items-center gap-1">
            <Lightbulb className="h-4 w-4" />
            Practical Notes
          </h4>
          <p className="text-sm text-muted-foreground">
            {recommendation.practical_notes}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export function DecisionSupport() {
  const [formData, setFormData] = useState<DecisionRequest>({
    task_type: '',
    dataset_size: 'medium',
    annotation_amount: 'moderate',
    image_type: 'natural',
    dimensionality: '2d',
    need_interpretability: false,
    real_time_required: false,
    accuracy_priority: 'balanced',
    problem_type: 'discriminative',
  });

  const { data: supportedOptions } = useQuery({
    queryKey: ['supported-tasks'],
    queryFn: getSupportedTasks,
  });

  const mutation = useMutation({
    mutationFn: getDecisionSupport,
    onError: (error) => {
      toast.error('Failed to get recommendations: ' + error.message);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.task_type) {
      toast.error('Please select a task type');
      return;
    }
    mutation.mutate(formData);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Decision Support</h1>
        <p className="text-muted-foreground">
          Get personalized recommendations for your computer vision project
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HelpCircle className="h-5 w-5" />
              Tell us about your project
            </CardTitle>
            <CardDescription>
              Answer a few questions to get tailored recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="task_type">Task Type *</Label>
                <Select
                  value={formData.task_type}
                  onValueChange={(v) => setFormData({ ...formData, task_type: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a task" />
                  </SelectTrigger>
                  <SelectContent>
                    {supportedOptions?.tasks.map((task) => (
                      <SelectItem key={task} value={task}>
                        {task}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="image_type">Image Type</Label>
                <Select
                  value={formData.image_type}
                  onValueChange={(v) => setFormData({ ...formData, image_type: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {supportedOptions?.image_types.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="dataset_size">Dataset Size</Label>
                  <Select
                    value={formData.dataset_size}
                    onValueChange={(v) => setFormData({ ...formData, dataset_size: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {supportedOptions?.dataset_sizes.map((size) => (
                        <SelectItem key={size} value={size}>
                          {size}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="annotation_amount">Annotation Amount</Label>
                  <Select
                    value={formData.annotation_amount}
                    onValueChange={(v) => setFormData({ ...formData, annotation_amount: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {supportedOptions?.annotation_amounts.map((amount) => (
                        <SelectItem key={amount} value={amount}>
                          {amount}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="dimensionality">Dimensionality</Label>
                <Select
                  value={formData.dimensionality}
                  onValueChange={(v) => setFormData({ ...formData, dimensionality: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="2d">2D Images</SelectItem>
                    <SelectItem value="3d">3D/Volumetric</SelectItem>
                    <SelectItem value="video">Video</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="accuracy_priority">Priority</Label>
                <Select
                  value={formData.accuracy_priority}
                  onValueChange={(v) => setFormData({ ...formData, accuracy_priority: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="speed">Speed</SelectItem>
                    <SelectItem value="balanced">Balanced</SelectItem>
                    <SelectItem value="accuracy">Maximum Accuracy</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="problem_type">Problem Type</Label>
                <Select
                  value={formData.problem_type}
                  onValueChange={(v) => setFormData({ ...formData, problem_type: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="discriminative">Discriminative</SelectItem>
                    <SelectItem value="generative">Generative</SelectItem>
                    <SelectItem value="both">Both</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="real_time"
                    checked={formData.real_time_required}
                    onCheckedChange={(v) => setFormData({ ...formData, real_time_required: v })}
                  />
                  <Label htmlFor="real_time">Real-time required</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="interpretability"
                    checked={formData.need_interpretability}
                    onCheckedChange={(v) => setFormData({ ...formData, need_interpretability: v })}
                  />
                  <Label htmlFor="interpretability">Need interpretability</Label>
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full"
                disabled={mutation.isPending}
              >
                {mutation.isPending ? 'Getting recommendations...' : 'Get Recommendations'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="space-y-6">
          {mutation.isPending ? (
            <div className="space-y-4">
              <Skeleton className="h-64" />
              <Skeleton className="h-64" />
            </div>
          ) : mutation.data ? (
            <>
              <Card className="bg-primary/5 border-primary">
                <CardHeader>
                  <CardTitle>Task Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>{mutation.data.task_summary}</p>
                </CardContent>
              </Card>

              <div>
                <h3 className="text-lg font-semibold mb-3">Primary Recommendations</h3>
                <div className="space-y-4">
                  {mutation.data.primary_recommendations.map((rec, i) => (
                    <RecommendationCard 
                      key={i} 
                      recommendation={rec} 
                      isPrimary={true}
                    />
                  ))}
                </div>
              </div>

              {mutation.data.alternative_approaches.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Alternative Approaches</h3>
                  <div className="space-y-4">
                    {mutation.data.alternative_approaches.map((rec, i) => (
                      <RecommendationCard 
                        key={i} 
                        recommendation={rec} 
                        isPrimary={false}
                      />
                    ))}
                  </div>
                </div>
              )}

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5" />
                    Data Preparation Tips
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                    {mutation.data.data_preparation_tips.map((tip, i) => (
                      <li key={i}>{tip}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Evaluation Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {mutation.data.evaluation_metrics.map((metric, i) => (
                      <Badge key={i} variant="secondary">{metric}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-muted">
                <CardHeader>
                  <CardTitle>Trade-offs Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground whitespace-pre-line">
                    {mutation.data.trade_offs_summary}
                  </p>
                </CardContent>
              </Card>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <HelpCircle className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium">No recommendations yet</h3>
              <p className="text-muted-foreground">
                Fill out the form to get personalized recommendations for your project
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
