from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post
from .forms import PostForm
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import PostSerializer
from django.db.models import Count, Max
from collections import defaultdict

def post_list(request):
    posts = Post.objects.all().order_by('-created_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


def js_test(request):
    return render(request, 'blog/js_test.html', {})

class BlogImages(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        검출 객체별 통계 API
        각 객체 클래스별 검출 횟수와 최근 검출 시간을 반환합니다.
        URL: /api_root/Post/stats/
        """
        # 모든 Post에서 title 필드를 기준으로 그룹화
        stats = Post.objects.values('title').annotate(
            count=Count('id'),
            last_detected=Max('created_date')
        ).order_by('-count')
        
        # 결과를 딕셔너리 형태로 정리
        result = {
            'total_detections': Post.objects.count(),
            'object_stats': []
        }
        
        for stat in stats:
            result['object_stats'].append({
                'object_name': stat['title'],
                'detection_count': stat['count'],
                'last_detected': stat['last_detected'].isoformat() if stat['last_detected'] else None
            })
        
        return Response(result)