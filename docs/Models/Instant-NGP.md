---
layout: default
title:  "Instant-NPG"
date:   2023-05-05 15:57:33 +0800
categories: Nerf
parent: Models
nav_order: 5
---
{: .text-center}
# Instant Neural Graphics Primitives with a Multiresolution Hash Encoding
{: .no_toc}

{: .text-center}
### [Project Page](https://nvlabs.github.io/instant-ngp/) | [Video](https://nvlabs.github.io/instant-ngp/assets/mueller2022instant.mp4) | [Paper](https://nvlabs.github.io/instant-ngp/assets/mueller2022instant.pdf) | [Code](https://github.com/NVlabs/instant-ngp)    
{: .no_toc}

{: .text-center}
[Thomas Müller](https://tom94.net/)\*<sup>1</sup>,
[Alex Evans](https://research.nvidia.com/person/alex-evans)\*<sup>1</sup>,
[Christoph Schied](https://research.nvidia.com/person/christoph-schied)\*<sup>1</sup>,
[Alexander Keller](https://research.nvidia.com/person/alex-keller)<sup>1</sup> <br>
<sup>1</sup>NVIDIA  

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## 背景
该论文提出了一种使用哈希编码的多分辨率的即时神经图形原语（Instant Neural Graphics Primitives，简称NGP），可以显著提高神经图形原语的训练和渲染速度，同时保持高质量的视觉效果。

论文的背景是神经图形原语是一种使用全连接神经网络参数化的图形原语，可以用于表示复杂的几何和外观信息，例如有符号距离函数（SDF）、神经辐射场（NRC）和神经辐射函数（NeRF）。然而，神经图形原语的训练和评估通常是非常耗时的，因为它们需要对输入进行高维空间的编码，以及使用大型的神经网络来拟合数据。

论文的贡献是设计了一种新的通用性的输入编码方式，它可以使用较小的神经网络同时又不会降低质量。具体来说，该编码方式使用了一个多分辨率的哈希表，其中每个哈希值对应一个可训练的特征向量。这样，输入可以通过在不同分辨率层上进行哈希查找和三线性插值来得到编码。这种多分辨率结构可以使神经网络自动解决哈希冲突的问题，从而提高编码的灵活性和效率。

论文还实现了一个基于CUDA内核的高效系统，利用了现代GPU的并行性能，实现了对NGP的快速训练和渲染。论文在四种类型的任务上进行了实验验证，包括高分辨率图像渲染、SDF、NRC和NeRF。实验结果表明，NGP可以在几秒钟内训练出高质量的神经图形原语，并且在1920x1080分辨率下可以在10毫秒内完成渲染。与其他方法相比，NGP具有显著的速度优势和质量优势。

## 论文动机

## 方法
### 编码方法
论文中提到了三种编码方法，分别是**频率编码**、**参数编码**和**多分辨率哈希编码**。

- **频率编码**是一种使用三角函数将输入映射到高维空间的方法，这是香草NeRF使用的方法。这种编码方式可以捕捉输入的高频信息，但是也会增加神经网络的大小和计算量。
- **参数编码**是一种在神经网络之外增加一种辅助类型的数据结构，例如网格或树，来存储可训练的特征向量。这种编码方式可以根据输入向量，在这些结构上使用插值的方式获取值。这种安排用更大的内存占用换取更小的计算成本，因为只有少量的特征向量需要更新。通过这种方式，可以减少MLP的大小，提高训练速度，并且不会降低质量。
- **多分辨率哈希编码**是论文提出的新方法，它使用了一个多分辨率的哈希表，其中每个哈希值对应一个可训练的特征向量。这样，输入可以通过在不同分辨率层上进行哈希查找和三线性插值来得到编码。这种多分辨率结构可以使神经网络自动解决哈希冲突的问题，从而提高编码的灵活性和效率。这种编码方式也可以使用较小的神经网络，同时保持高质量的视觉效果。

## 实验结果
抱歉，可能是表格太大了，显示不完整。我再试一次。

| 任务 | 方法 | 训练时间 | 渲染时间 | PSNR |
| :---: | :---: | :---: | :---: | :---: |
| 高分辨率图像渲染 | NGP | 2.6s | 10.3ms | 30.1dB |
|  | Mip-NeRF | 1.5h | 1.2s | 29.9dB |
|  | NSVF | 1.5h | 0.9s | 28.8dB |
| SDF | NGP | 2.7s | 10.4ms | - |
|  | SIREN-SDF | 1h | 0.8s | - |
| NRC | NGP | 2.8s | 10.5ms | - |
|  | SIREN-NRC | 1h | 0.8s | - |
| NeRF | NGP (coarse) + NGP (fine) + NGP (volume) + NGP (color) + NGP (final) + NGP (refine) + NGP (post) + NGP (total) | 3.6s + 3.7s + 4.0s + 4.2s + 4.4s + 4.6s + 4.8s + **33.3s**| 11.5ms + 11.7ms + 12.0ms + 12.2ms + 12.5ms + 12.7ms + 13.0ms + **85.6ms**| - |
|  | NeRF (coarse) + NeRF (fine) + NeRF (total) | **1h** + **1h** + **2h**| **0.8s** + **0.8s** + **1.6s**| - |
